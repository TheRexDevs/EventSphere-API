"""
Event Management Controller for Admin API

Handles event CRUD operations, approval workflow, and event management
for administrators and organizers.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional, cast
from datetime import datetime

from flask import request, current_app, Flask
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from pydantic import ValidationError
from werkzeug.datastructures import FileStorage
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid
from io import BytesIO

from app.extensions import db
from app.models.event import Event, EventCategory
from app.models.media import Media
from app.models.user import AppUser
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils
from app.utils.helpers.user import get_current_user
from app.schemas.event import CreateEventRequest, UpdateEventRequest, CreateEventWithFilesRequest, UpdateEventWithFilesRequest
from app.logging import log_error
from app.utils.media_service.uploaders import CloudinaryUploader


class EventController:
    """Controller for event management operations."""

    @staticmethod
    def _upload_image_background(app: Flask, file: FileStorage, filename: str, event_id: str, is_featured: bool = False) -> None:
        """Upload image to Cloudinary in background thread within app context."""
        try:
            with app.app_context():
                uploader = CloudinaryUploader()
                result = uploader.upload_to_cloudinary(
                    file=file,
                    public_id=filename.rsplit('.', 1)[0],  # Remove extension for public_id
                    folder='events',
                    resource_type='image',
                    optimization=True
                )

                if result:
                    # Create media record
                    media = Media()
                    media.filename = filename
                    media.original_filename = file.filename or filename
                    media.file_path = result.get('public_id', filename)
                    media.file_url = result['secure_url']
                    media.thumbnail_url = result.get('thumbnail_url')
                    media.width = result.get('width')
                    media.height = result.get('height')
                    media.file_type = 'image'
                    media.file_size = result.get('bytes', 0)
                    media.mime_type = f"image/{result.get('format', 'jpeg')}"
                    media.file_extension = f".{result.get('format', 'jpg')}"
                    media.event_id = uuid.UUID(event_id)
                    media.cloudinary_public_id = result.get('public_id', '')
                    media.cloudinary_folder = 'events'

                    if is_featured:
                        media.is_featured = True

                    db.session.add(media)
                    db.session.commit()

                    # Update event's featured_image_id if this is the featured image
                    if is_featured:
                        event = Event.query.get(uuid.UUID(event_id))
                        if event:
                            event.featured_image_id = media.id
                            db.session.commit()
        except Exception as e:
            log_error(f"Failed to upload image {filename} for event {event_id}", e)

    @staticmethod
    def _process_form_data_files(request, event_id: str) -> Dict[str, Any]:
        """Process uploaded files from FormData and start background uploads."""
        featured_image = request.files.get('featured_image')
        gallery_images = request.files.getlist('gallery_images[]') if 'gallery_images[]' in request.files else []

        uploaded_urls = {'featured_image': None, 'gallery_images': []}

        # Handle featured image upload
        if featured_image and featured_image.filename:
            # Read file content into memory for background processing
            featured_image.stream.seek(0)
            file_content = featured_image.stream.read()
            featured_image.stream.seek(0)  # Reset for potential other uses
            
            # Create new FileStorage with content in memory
            file_copy = FileStorage(
                stream=BytesIO(file_content),
                filename=featured_image.filename,
                content_type=featured_image.content_type
            )
            
            filename = f"event_{event_id}_featured_{uuid.uuid4().hex[:8]}.{featured_image.filename.rsplit('.', 1)[1].lower()}"
            # Start background upload
            # mypy-friendly: current_app may be LocalProxy; use getattr fallback without calling unknown attribute directly
            app_getter1 = getattr(current_app, "_get_current_object", None)
            app_instance1: Flask = cast(Flask, app_getter1()) if callable(app_getter1) else cast(Flask, current_app)
            threading.Thread(
                target=EventController._upload_image_background,
                args=(app_instance1, file_copy, filename, event_id, True)
            ).start()
            uploaded_urls['featured_image'] = f"uploading:{filename}"

        # Handle gallery images upload
        for i, gallery_image in enumerate(gallery_images):
            if gallery_image and gallery_image.filename:
                # Read file content into memory for background processing
                gallery_image.stream.seek(0)
                file_content = gallery_image.stream.read()
                gallery_image.stream.seek(0)  # Reset for potential other uses
                
                # Create new FileStorage with content in memory
                file_copy = FileStorage(
                    stream=BytesIO(file_content),
                    filename=gallery_image.filename,
                    content_type=gallery_image.content_type
                )
                
                filename = f"event_{event_id}_gallery_{i}_{uuid.uuid4().hex[:8]}.{gallery_image.filename.rsplit('.', 1)[1].lower()}"
                # Start background upload
                app_getter2 = getattr(current_app, "_get_current_object", None)
                app_instance2: Flask = cast(Flask, app_getter2()) if callable(app_getter2) else cast(Flask, current_app)
                threading.Thread(
                    target=EventController._upload_image_background,
                    args=(app_instance2, file_copy, filename, event_id, False)
                ).start()
                uploaded_urls['gallery_images'].append(f"uploading:{filename}")

        return uploaded_urls

    @staticmethod
    def create_event():
        """Create a new event (Organizer/Admin only)."""
        try:
            # Check if request is FormData (multipart/form-data) or JSON
            content_type = request.content_type or ''

            if 'multipart/form-data' in content_type:
                # Handle FormData with file uploads
                return EventController._create_event_with_files()
            else:
                # Handle JSON request (existing functionality)
                return EventController._create_event_json()

        except Exception as e:
            log_error("Failed to create event", e)
            return error_response(f"Failed to create event: {str(e)}", 500)

    @staticmethod
    def _create_event_json():
        """Create event from JSON request (existing functionality)."""
        try:
            # Validate request data using Pydantic schema
            payload = CreateEventRequest.model_validate(request.get_json())

            # Get current user
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Create event with validated data
            event = Event()
            event.title = payload.title
            event.description = payload.description
            event.date = datetime.fromisoformat(payload.date).date()
            # Handle both HH:MM:SS and HH:MM formats
            try:
                event.time = datetime.strptime(payload.time, '%H:%M:%S').time()
            except ValueError:
                event.time = datetime.strptime(payload.time, '%H:%M').time()
            event.venue = payload.venue
            event.capacity = payload.capacity
            event.max_participants = payload.max_participants
            event.organizer_id = current_user.id

            # Set category if provided
            if payload.category_id:
                category = EventCategory.query.get(payload.category_id)
                if category:
                    event.category_id = payload.category_id

            # Handle featured image and gallery images
            if payload.featured_image_url:
                # Find or create media entry for featured image
                featured_media = Media.query.filter_by(file_url=payload.featured_image_url).first()
                if featured_media:
                    event.featured_image_id = featured_media.id
                    featured_media.mark_featured(True)

            # Handle gallery images
            if payload.gallery_image_urls:
                for image_url in payload.gallery_image_urls:
                    gallery_media = Media.query.filter_by(file_url=image_url).first()
                    if gallery_media and gallery_media.event_id == event.id:
                        # Mark as not featured (gallery image)
                        gallery_media.mark_featured(False)

            db.session.add(event)
            db.session.commit()

            # Reload event with media relationships for proper serialization
            db.session.refresh(event)
            return success_response(
                "Event created successfully. Pending admin approval.",
                201,
                {"event": event.to_dict()}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {str(e)}", 400)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def _create_event_with_files():
        """Create event from FormData with file uploads."""
        try:
            # Get current user
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Validate form data using Pydantic schema
            capacity_str = request.form.get('capacity', '0')
            max_participants_str = request.form.get('max_participants', '0')
            
            form_data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'date': request.form.get('date'),
                'time': request.form.get('time'),
                'venue': request.form.get('venue'),
                'capacity': int(capacity_str) if capacity_str and capacity_str.isdigit() else 0,
                'max_participants': int(max_participants_str) if max_participants_str and max_participants_str.isdigit() else 0,
                'category_id': request.form.get('category_id')
            }

            payload = CreateEventWithFilesRequest.model_validate(form_data)

            # Create event with validated data
            event = Event()
            event.title = payload.title
            event.description = payload.description
            event.date = datetime.fromisoformat(payload.date).date()
            # Handle both HH:MM:SS and HH:MM formats
            try:
                event.time = datetime.strptime(payload.time, '%H:%M:%S').time()
            except ValueError:
                event.time = datetime.strptime(payload.time, '%H:%M').time()
            event.venue = payload.venue
            event.capacity = payload.capacity
            event.max_participants = payload.max_participants
            event.organizer_id = current_user.id

            # Set category if provided
            if payload.category_id:
                try:
                    category_uuid = uuid.UUID(payload.category_id)
                    category = EventCategory.query.get(category_uuid)
                    if category:
                        event.category_id = category_uuid
                except ValueError:
                    pass  # Invalid UUID, ignore

            db.session.add(event)
            db.session.commit()

            # Process uploaded files in background
            upload_result = EventController._process_form_data_files(request, str(event.id))

            # Reload event with media relationships for proper serialization
            db.session.refresh(event)
            event_data = event.to_dict()

            # Add upload status to response
            event_data['upload_status'] = {
                'featured_image': upload_result['featured_image'],
                'gallery_images': upload_result['gallery_images'],
                'message': 'Images are being uploaded to Cloudinary in the background'
            }

            return success_response(
                "Event created successfully with image uploads. Images are processing in background.",
                201,
                {"event": event_data}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {str(e)}", 400)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_events():
        """Get all events with filtering and pagination."""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            status = request.args.get('status')
            organizer_id = request.args.get('organizer_id')
            search = request.args.get('search')

            # Build query
            query = Event.query

            if status:
                query = query.filter_by(status=status)

            if organizer_id:
                query = query.filter_by(organizer_id=uuid.UUID(organizer_id))

            if search:
                query = query.filter(
                    or_(
                        Event.title.ilike(f'%{search}%'),
                        Event.description.ilike(f'%{search}%'),
                        Event.venue.ilike(f'%{search}%')
                    )
                )

            # Paginate
            events = query.order_by(Event.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(
                "Events retrieved successfully",
                200,
                {
                    'events': [event.to_dict() for event in events.items],
                    'pagination': {
                        'page': events.page,
                        'per_page': events.per_page,
                        'total': events.total,
                        'pages': events.pages,
                        'has_next': events.has_next,
                        'has_prev': events.has_prev
                    }
                }
            )

        except Exception as e:
            return error_response(f"Failed to retrieve events: {str(e)}", 500)

    @staticmethod
    def get_event(event_id: str):
        """Get a specific event by ID."""
        try:
            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            return success_response(
                "Event retrieved successfully",
                200,
                {"event": event.to_dict()}
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            return error_response(f"Failed to retrieve event: {str(e)}", 500)

    @staticmethod
    def update_event(event_id: str):
        """Update an existing event."""
        try:
            # Check if request is FormData (multipart/form-data) or JSON
            content_type = request.content_type or ''

            if 'multipart/form-data' in content_type:
                # Handle FormData with file uploads
                return EventController._update_event_with_files(event_id)
            else:
                # Handle JSON request (existing functionality)
                return EventController._update_event_json(event_id)

        except Exception as e:
            log_error("Failed to update event", e)
            return error_response(f"Failed to update event: {str(e)}", 500)

    @staticmethod
    def _update_event_json(event_id: str):
        """Update event from JSON request (existing functionality)."""
        try:
            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Only organizer or admin can update
            if (event.organizer_id != current_user.id):
                return error_response("Insufficient permissions", 403)

            # Validate request data using Pydantic schema
            payload = UpdateEventRequest.model_validate(request.get_json())

            # Update fields with validated data
            if payload.title is not None:
                event.title = payload.title
            if payload.description is not None:
                event.description = payload.description
            if payload.date is not None:
                event.date = datetime.fromisoformat(payload.date).date()
            if payload.time is not None:
                # Handle both HH:MM:SS and HH:MM formats
                time_str = payload.time or ""
                if time_str:
                    try:
                        event.time = datetime.strptime(time_str, '%H:%M:%S').time()
                    except ValueError:
                        event.time = datetime.strptime(time_str, '%H:%M').time()
            if payload.venue is not None:
                event.venue = payload.venue
            if payload.capacity is not None:
                event.capacity = payload.capacity
            if payload.max_participants is not None:
                event.max_participants = payload.max_participants
            if payload.category_id is not None:
                category = EventCategory.query.get(payload.category_id)
                if category:
                    event.category_id = payload.category_id

            # Handle featured image update
            if payload.featured_image_url is not None:
                if payload.featured_image_url:
                    # Find or create media entry for featured image
                    featured_media = Media.query.filter_by(file_url=payload.featured_image_url).first()
                    if featured_media:
                        event.featured_image_id = featured_media.id
                        featured_media.mark_featured(True)
                else:
                    # Remove featured image
                    event.featured_image_id = None

            # Handle gallery images update
            if payload.gallery_image_urls is not None:
                # Reset all current gallery images to not featured
                for media in event.safe_media_list:
                    if hasattr(media, 'is_featured') and not media.is_featured:
                        media.mark_featured(False)

                # Mark new gallery images
                for image_url in payload.gallery_image_urls:
                    gallery_media = Media.query.filter_by(file_url=image_url).first()
                    if gallery_media and gallery_media.event_id == event.id:
                        gallery_media.mark_featured(False)  # Ensure it's marked as gallery image

            event.updated_at = DateTimeUtils.aware_utcnow()
            db.session.commit()

            # Reload event with media relationships for proper serialization
            db.session.refresh(event)
            return success_response(
                "Event updated successfully",
                200,
                {"event": event.to_dict()}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {str(e)}", 400)
        except ValueError:
            return error_response("Invalid data format", 400)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def _update_event_with_files(event_id: str):
        """Update event from FormData with file uploads."""
        try:
            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Only organizer or admin can update
            # if (event.organizer_id != current_user.id):
            #     return error_response("Insufficient permissions", 403)

            # Validate form data using Pydantic schema
            form_data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'date': request.form.get('date'),
                'time': request.form.get('time'),
                'venue': request.form.get('venue'),
                'capacity': request.form.get('capacity'),
                'max_participants': request.form.get('max_participants'),
                'category_id': request.form.get('category_id')
            }

            # Convert string values to appropriate types - handle None values
            capacity_str = form_data.get('capacity')
            max_participants_str = form_data.get('max_participants')
            
            # Create new dict to avoid type conflicts
            validated_data = {}
            for key, value in form_data.items():
                if key in ['capacity', 'max_participants']:
                    if value and str(value).isdigit():
                        validated_data[key] = int(value)
                    else:
                        validated_data[key] = None
                else:
                    validated_data[key] = value

            payload = UpdateEventWithFilesRequest.model_validate(validated_data)

            # Update fields with validated data
            if payload.title is not None:
                event.title = payload.title
            if payload.description is not None:
                event.description = payload.description
            if payload.date is not None:
                event.date = datetime.fromisoformat(payload.date).date()
            if payload.time is not None:
                # Handle both HH:MM:SS and HH:MM formats
                time_str = payload.time or ""
                if time_str:
                    try:
                        event.time = datetime.strptime(time_str, '%H:%M:%S').time()
                    except ValueError:
                        event.time = datetime.strptime(time_str, '%H:%M').time()
            if payload.venue is not None:
                event.venue = payload.venue
            if payload.capacity is not None:
                event.capacity = payload.capacity
            if payload.max_participants is not None:
                event.max_participants = payload.max_participants
            if payload.category_id is not None:
                try:
                    category_uuid = uuid.UUID(payload.category_id)
                    category = EventCategory.query.get(category_uuid)
                    if category:
                        event.category_id = category_uuid
                except ValueError:
                    pass  # Invalid UUID, ignore

            event.updated_at = DateTimeUtils.aware_utcnow()
            db.session.commit()

            # Process uploaded files in background
            upload_result = EventController._process_form_data_files(request, str(event.id))

            # Reload event with media relationships for proper serialization
            db.session.refresh(event)
            event_data = event.to_dict()

            # Add upload status to response
            event_data['upload_status'] = {
                'featured_image': upload_result['featured_image'],
                'gallery_images': upload_result['gallery_images'],
                'message': 'Images are being uploaded to Cloudinary in the background'
            }

            return success_response(
                "Event updated successfully with image uploads. Images are processing in background.",
                200,
                {"event": event_data}
            )

        except ValidationError as e:
            log_error("Validation error", e)
            return error_response(f"Validation error: {str(e)}", 400)
        except ValueError as e:
            log_error("Invalid data format", e)
            return error_response("Invalid data format", 400)
        except Exception as e:
            log_error("Failed to update event", e)
            db.session.rollback()
            raise e

    @staticmethod
    def delete_event(event_id: str):
        """Delete an event."""
        try:
            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Only organizer or admin can delete
            if (event.organizer_id != current_user.id):
                return error_response("Insufficient permissions", 403)

            db.session.delete(event)
            db.session.commit()

            return success_response("Event deleted successfully", 200)

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete event: {str(e)}", 500)

    @staticmethod
    def approve_event(event_id: str):
        """Approve a pending event (Admin only)."""
        try:
            current_user = get_current_user()
            if not current_user:
                return error_response("Admin access required", 403)

            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            if event.status != 'pending':
                return error_response("Event is not pending approval", 400)

            event.status = 'approved'
            event.updated_at = DateTimeUtils.aware_utcnow()
            db.session.commit()

            return success_response(
                "Event approved successfully",
                200,
                {"event": event.to_dict()}
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to approve event: {str(e)}", 500)

    @staticmethod
    def publish_event(event_id: str):
        """Publish/unpublish an approved event."""
        try:
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Only organizer or admin can publish/unpublish
            if (event.organizer_id != current_user.id):
                return error_response("Insufficient permissions", 403)

            # Toggle publish status (assuming we add a published field)
            # For now, just return success
            return success_response(
                "Event publish status updated",
                200,
                {"event": event.to_dict()}
            )

        except Exception as e:
            return error_response(f"Failed to update publish status: {str(e)}", 500)

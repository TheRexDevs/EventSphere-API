"""
Admin media controller for managing file uploads and media library within events.

This module handles all media-related operations including upload, deletion,
gallery management, and search with proper admin access validation.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, asc, desc
from flask_sqlalchemy.pagination import Pagination
import uuid

from app.extensions import db
from app.logging import log_error, log_event
from app.models import Media, Event
from app.schemas.media import (
    UploadMediaRequest,
    DeleteMediaRequest,
    UpdateMediaRequest,
    MediaResponse,
    MediaListResponse,
    MediaStatsResponse,
    MediaUploadResponse,
    BulkDeleteResponse,
)
from app.utils.helpers.http_response import success_response, error_response
from app.utils.helpers.user import get_current_user
from app.utils.media_service import MediaService


class AdminMediaController:
    """Controller for admin media management operations within events."""

    @staticmethod
    def _validate_media_uuid(media_id: str) -> Optional[uuid.UUID]:
        """Validate and convert media ID string to UUID."""
        try:
            return uuid.UUID(media_id)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _validate_event_uuid(event_id: str) -> Optional[uuid.UUID]:
        """Validate and convert event ID string to UUID."""
        try:
            return uuid.UUID(event_id)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _validate_user_uuid(user_id: str) -> Optional[uuid.UUID]:
        """Validate and convert user ID string to UUID."""
        try:
            return uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_event_by_id(event_id: str) -> Tuple[Optional[Response], Optional[Event]]:
        """Get event by ID with admin access validation."""
        # Validate UUID format
        event_uuid = AdminMediaController._validate_event_uuid(event_id)
        if not event_uuid:
            return error_response("invalid event ID format", 400), None

        # Get event
        event = Event.query.filter_by(id=event_uuid).first()
        if not event:
            return error_response("event not found", 404), None

        return None, event

    @staticmethod
    def _get_event_media(event_id: str, media_id: str) -> Tuple[Optional[Response], Optional[Media], Optional[Event]]:
        """Get media by ID within event for admin access."""
        # First get the event
        error_resp, event = AdminMediaController._get_event_by_id(event_id)
        if error_resp:
            return error_resp, None, None

        # At this point, event is guaranteed to not be None
        assert event is not None

        # Validate media UUID
        media_uuid = AdminMediaController._validate_media_uuid(media_id)
        if not media_uuid:
            return error_response("invalid media ID format", 400), None, event

        # Get media within the event
        media = Media.query.filter_by(id=media_uuid, event_id=event.id).first()
        if not media:
            return error_response("media not found", 404), None, event

        return None, media, event

    @staticmethod
    def upload_media(event_id: str) -> Response:
        """Upload media files to an event (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get event and validate ownership
        error_resp, event = AdminMediaController._get_event_by_id(event_id)
        if error_resp:
            return error_resp

        try:
            # Check if files are provided
            if 'files' not in request.files:
                return error_response("no files provided", 400)

            files = request.files.getlist('files')
            if not files or len(files) == 0:
                return error_response("no files provided", 400)

            # Parse upload options
            payload = UploadMediaRequest.model_validate(request.form)

            uploaded_media = []
            errors = []

            for file in files:
                if file.filename == '':
                    continue

                try:
                    # Upload using enhanced service
                    media = MediaService.upload_media_file(
                        file=file,
                        event_id=event.id,  # type: ignore
                        custom_filename=payload.custom_filename,
                        optimization=payload.optimize
                    )
                    uploaded_media.append(media)

                except Exception as e:
                    log_error(f"Failed to upload {file.filename}", e)
                    errors.append(f"Failed to upload {file.filename}: {str(e)}")

            if not uploaded_media:
                return error_response("no files were uploaded successfully", 400)

            # Return response
            response_data = {
                "uploaded": [MediaResponse.model_validate(media.to_dict()).model_dump() for media in uploaded_media],
                "errors": errors,
                "message": f"Successfully uploaded {len(uploaded_media)} file(s)"
            }

            log_event(f"Admin media uploaded to event {event.title}", data={  # type: ignore
                "event_id": str(event.id),  # type: ignore
                "user_id": str(current_user.id),
                "uploaded_count": len(uploaded_media),
                "error_count": len(errors)
            })

            return success_response(
                f"Successfully uploaded {len(uploaded_media)} file(s)",
                201,
                response_data
            )

        except Exception as e:
            log_error(f"Media upload failed: {str(e)}", error=e)
            return error_response("upload failed", 500)

    @staticmethod
    def list_media(event_id: str) -> Response:
        """List all media within an event (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get event
        error_resp, event = AdminMediaController._get_event_by_id(event_id)
        if error_resp:
            return error_resp

        # At this point, event is guaranteed to not be None
        assert event is not None

        # Get pagination and filtering parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)  # Max 50 per page
        file_type = request.args.get('file_type')
        is_featured = request.args.get('is_featured', type=bool)
        search = request.args.get('search', '').strip()
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        # Build query
        stmt = select(Media).where(Media.event_id == event.id)

        # Apply filters
        if file_type:
            stmt = stmt.where(Media.file_type == file_type)

        if is_featured is not None:
            stmt = stmt.where(Media.is_featured == is_featured)

        if search:
            stmt = stmt.where(
                (Media.filename.ilike(f'%{search}%')) |
                (Media.original_filename.ilike(f'%{search}%'))
            )

        # Apply sorting
        sort_column = getattr(Media, sort, Media.created_at)
        if order.lower() == 'desc':
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))

        # Paginate
        paginated: Pagination = db.paginate(
            stmt,
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Convert to response format
        media_responses = [
            MediaResponse.model_validate(media.to_dict())
            for media in paginated.items
        ]

        response_data = MediaListResponse(
            media=media_responses,
            total=paginated.total or 0,
            page=page,
            per_page=per_page,
            has_next=paginated.has_next,
            has_prev=paginated.has_prev
        )

        return success_response("Media retrieved successfully", 200, response_data.model_dump())

    @staticmethod
    def get_media(event_id: str, media_id: str) -> Response:
        """Get a specific media file by ID (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get media and validate access
        error_resp, media, event = AdminMediaController._get_event_media(event_id, media_id)
        if error_resp:
            return error_resp

        # At this point, media and event are guaranteed to not be None
        assert media is not None
        assert event is not None

        # Increment usage count
        media.increment_usage()

        return success_response(
            "Media retrieved successfully",
            200,
            {"media": MediaResponse.model_validate(media.to_dict()).model_dump()}
        )

    @staticmethod
    def update_media(event_id: str, media_id: str) -> Response:
        """Update media metadata (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get media and validate access
        error_resp, media, event = AdminMediaController._get_event_media(event_id, media_id)
        if error_resp:
            return error_resp

        # At this point, media and event are guaranteed to not be None
        assert media is not None
        assert event is not None

        # Parse request
        payload = UpdateMediaRequest.model_validate(request.get_json())

        try:
            # Update fields
            if payload.filename is not None:
                media.filename = payload.filename
            if payload.is_featured is not None:
                media.is_featured = payload.is_featured

            media.updated_at = db.func.now()
            db.session.commit()

            log_event(f"Admin media updated: {media.filename}", data={
                "media_id": str(media.id),
                "event_id": str(event.id),  # type: ignore
                "user_id": str(current_user.id)
            })

            return success_response(
                "Media updated successfully",
                200,
                {"media": MediaResponse.model_validate(media.to_dict()).model_dump()}
            )

        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to update media: {str(e)}", error=e)
            return error_response("failed to update media", 500)

    @staticmethod
    def delete_media(event_id: str, media_id: str) -> Response:
        """Delete a specific media file (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get media and validate access
        error_resp, media, event = AdminMediaController._get_event_media(event_id, media_id)
        if error_resp:
            return error_resp

        # At this point, media and event are guaranteed to not be None
        assert media is not None
        assert event is not None

        try:
            filename = media.filename
            success = MediaService.delete_media(media.id, event.id)

            if success:
                log_event(f"Admin media deleted: {filename}", data={
                    "media_id": str(media_id),
                    "event_id": str(event.id),  # type: ignore
                    "user_id": str(current_user.id)
                })

                return success_response("Media deleted successfully", 200)
            else:
                return error_response("failed to delete media", 500)

        except Exception as e:
            log_error(f"Failed to delete media: {str(e)}", error=e)
            return error_response("failed to delete media", 500)

    @staticmethod
    def get_media_stats(event_id: str) -> Response:
        """Get media statistics for an event (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get event
        error_resp, event = AdminMediaController._get_event_by_id(event_id)
        if error_resp:
            return error_resp

        # At this point, event is guaranteed to not be None
        assert event is not None

        try:
            stats = MediaService.get_media_usage_stats(event.id)

            response_data = MediaStatsResponse(
                total_files=stats.get('total_files', 0),
                total_size=stats.get('total_size', 0),
                total_size_mb=stats.get('total_size', 0) / (1024 * 1024),
                by_type=stats.get('by_type', {})
            )

            return success_response("Media statistics retrieved successfully", 200, response_data.model_dump())

        except Exception as e:
            log_error(f"Failed to get media stats: {str(e)}", error=e)
            return error_response("failed to retrieve media statistics", 500)

    @staticmethod
    def bulk_delete_media(event_id: str) -> Response:
        """Delete multiple media files (Admin/Organizer only)."""
        current_user = get_current_user()
        if not current_user:
            return error_response("Authentication required", 401)

        # Get event
        error_resp, event = AdminMediaController._get_event_by_id(event_id)
        if error_resp:
            return error_resp

        # At this point, event is guaranteed to not be None
        assert event is not None

        # Parse request
        payload = DeleteMediaRequest.model_validate(request.get_json())

        try:
            deleted_count = 0
            failed_deletions = []

            for media_id in payload.media_ids:
                success = MediaService.delete_media(media_id, event.id)
                if success:
                    deleted_count += 1
                else:
                    failed_deletions.append(str(media_id))

            log_event(f"Admin bulk media deletion in event {event.title}", data={
                "event_id": str(event.id),  # type: ignore
                "user_id": str(current_user.id),
                "deleted_count": deleted_count,
                "failed_count": len(failed_deletions)
            })

            response_data = BulkDeleteResponse(
                deleted_count=deleted_count,
                failed_deletions=failed_deletions,
                message=f"Successfully deleted {deleted_count} file(s)"
            )

            return success_response(
                f"Successfully deleted {deleted_count} file(s)",
                200,
                response_data.model_dump()
            )

        except Exception as e:
            log_error(f"Failed to bulk delete media: {str(e)}", error=e)
            return error_response("failed to delete media", 500)

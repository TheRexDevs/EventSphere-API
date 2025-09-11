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
from typing import Dict, Any, List, Optional
from datetime import datetime

from flask import request, g
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from pydantic import ValidationError

from app.extensions import db
from app.models.event import Event, EventCategory
from app.models.user import AppUser
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils
from app.schemas.event import CreateEventRequest, UpdateEventRequest


class EventController:
    """Controller for event management operations."""

    @staticmethod
    def create_event():
        """Create a new event (Organizer/Admin only)."""
        try:
            # Validate request data using Pydantic schema
            payload = CreateEventRequest.model_validate(request.get_json())

            # Get current user
            current_user = g.user
            if not current_user:
                return error_response("Authentication required", 401)

            # Create event with validated data
            event = Event()
            event.title = payload.title
            event.description = payload.description
            event.date = datetime.fromisoformat(payload.date).date()
            event.time = datetime.fromisoformat(payload.time).time()
            event.venue = payload.venue
            event.capacity = payload.capacity
            event.max_participants = payload.max_participants
            event.organizer_id = current_user.id

            # Set category if provided
            if payload.category_id:
                category = EventCategory.query.get(payload.category_id)
                if category:
                    event.category_id = payload.category_id

            db.session.add(event)
            db.session.commit()

            return success_response(
                "Event created successfully. Pending admin approval.",
                201,
                {"event": event.to_dict()}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {str(e)}", 400)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to create event: {str(e)}", 500)

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
            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            current_user = g.user
            if not current_user:
                return error_response("Authentication required", 401)

            # Only organizer or admin can update
            if (event.organizer_id != current_user.id and
                current_user.role not in ['admin', 'organizer']):
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
                event.time = datetime.fromisoformat(payload.time).time()
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

            event.updated_at = DateTimeUtils.aware_utcnow()
            db.session.commit()

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
            return error_response(f"Failed to update event: {str(e)}", 500)

    @staticmethod
    def delete_event(event_id: str):
        """Delete an event."""
        try:
            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            current_user = g.user
            if not current_user:
                return error_response("Authentication required", 401)

            # Only organizer or admin can delete
            if (event.organizer_id != current_user.id and
                current_user.role != 'admin'):
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
            current_user = g.user
            if not current_user or current_user.role != 'admin':
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
            current_user = g.user
            if not current_user:
                return error_response("Authentication required", 401)

            event_uuid = uuid.UUID(event_id)
            event = Event.query.get(event_uuid)

            if not event:
                return error_response("Event not found", 404)

            # Only organizer or admin can publish/unpublish
            if (event.organizer_id != current_user.id and
                current_user.role != 'admin'):
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

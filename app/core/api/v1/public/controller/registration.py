"""
Registration Controller

Handles event registration operations for participants,
including capacity management and registration tracking.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime

from flask import request, g

from app.extensions import db
from app.models.event import Event
from app.models.registration import Registration
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils
from app.logging import log_error
from app.utils.helpers.user import get_current_user


class RegistrationController:
    """Controller for event registration operations."""

    @staticmethod
    def register_for_event(event_id: str):
        """Register the current user for an event."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = get_current_user()

            if not current_user:
                return error_response("Authentication required", 401)

            # Check if event exists and is approved
            event: Event | None = Event.query.filter_by(
                id=event_uuid,
                status='approved'
            ).first()

            if not event:
                return error_response("Event not found or not available", 404)

            # Check if user is already registered
            existing_registration = Registration.query.filter_by(
                event_id=event_uuid,
                student_id=current_user.id
            ).first()

            if existing_registration:
                if existing_registration.status == 'confirmed':
                    return error_response("Already registered for this event", 409)
                elif existing_registration.status == 'cancelled':
                    # Reactivate cancelled registration
                    existing_registration.status = 'confirmed'
                    existing_registration.registered_on = DateTimeUtils.aware_utcnow()
                    db.session.commit()
                    return success_response("Registration reactivated successfully", 200)

            # Check capacity
            confirmed_registrations = Registration.query.filter_by(
                event_id=event_uuid,
                status='confirmed'
            ).count()

            if event.max_participants > 0 and confirmed_registrations >= event.max_participants:
                return error_response("Event is full", 409)

            # Create new registration
            registration = Registration()
            registration.event_id=event_uuid
            registration.student_id=current_user.id
            registration.status='confirmed'

            db.session.add(registration)
            db.session.commit()

            return success_response(
                "Successfully registered for event",
                201,
                {"registration": registration.to_dict()}
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            db.session.rollback()
            log_error("Failed to register", e)
            return error_response(f"Failed to register: {str(e)}", 500)

    @staticmethod
    def cancel_registration(event_id: str):
        """Cancel registration for an event."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = get_current_user()

            if not current_user:
                return error_response("Authentication required", 401)

            # Find the registration
            registration = Registration.query.filter_by(
                event_id=event_uuid,
                student_id=current_user.id,
                status='confirmed'
            ).first()

            if not registration:
                return error_response("Registration not found", 404)

            # Cancel the registration
            registration.status = 'cancelled'
            db.session.commit()

            return success_response("Registration cancelled successfully", 200)

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to cancel registration: {str(e)}", 500)

    @staticmethod
    def get_user_registrations():
        """Get current user's registrations."""
        try:
            current_user = get_current_user()

            if not current_user:
                return error_response("Authentication required", 401)

            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            status = request.args.get('status', 'confirmed')

            # Build query
            query = Registration.query.filter_by(student_id=current_user.id)

            if status:
                query = query.filter_by(status=status)

            # Paginate
            registrations = query.order_by(Registration.registered_on.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(
                "Registrations retrieved successfully",
                200,
                {
                    'registrations': [reg.to_dict() for reg in registrations.items],
                    'pagination': {
                        'page': registrations.page,
                        'per_page': registrations.per_page,
                        'total': registrations.total,
                        'pages': registrations.pages,
                        'has_next': registrations.has_next,
                        'has_prev': registrations.has_prev
                    }
                }
            )

        except Exception as e:
            return error_response(f"Failed to retrieve registrations: {str(e)}", 500)

    @staticmethod
    def get_registration_details(registration_id: str):
        """Get details of a specific registration."""
        try:
            registration_uuid = uuid.UUID(registration_id)
            current_user = get_current_user()

            if not current_user:
                return error_response("Authentication required", 401)

            # Find the registration
            registration = Registration.query.filter_by(
                id=registration_uuid,
                student_id=current_user.id
            ).first()

            if not registration:
                return error_response("Registration not found", 404)

            return success_response(
                "Registration details retrieved successfully",
                200,
                {"registration": registration.to_dict()}
            )

        except ValueError:
            return error_response("Invalid registration ID format", 400)
        except Exception as e:
            return error_response(f"Failed to retrieve registration: {str(e)}", 500)

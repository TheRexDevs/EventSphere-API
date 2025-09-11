"""
Public Feedback Controller

Handles feedback submission for authenticated participants.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional

from flask import request, g

from app.extensions import db
from app.models.event import Event
from app.models.feedback import Feedback
from app.models.attendance import Attendance
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils
from app.schemas.feedback import SubmitFeedbackRequest, UpdateFeedbackRequest


class PublicFeedbackController:
    """Controller for public feedback operations."""

    @staticmethod
    def submit_feedback(event_id: str):
        """Submit feedback for an event (Participant only)."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Validate request data using Pydantic schema
            payload = SubmitFeedbackRequest.model_validate(request.get_json())

            # Verify event exists and is approved
            event = Event.query.filter_by(
                id=event_uuid,
                status='approved'
            ).first()

            if not event:
                return error_response("Event not found or not available for feedback", 404)

            # Check if user attended the event (optional - we can allow feedback without attendance)
            attendance = Attendance.query.filter_by(
                event_id=event_uuid,
                student_id=current_user.id,
                attended=True
            ).first()

            # Check if user already submitted feedback
            existing_feedback = Feedback.query.filter_by(
                event_id=event_uuid,
                student_id=current_user.id
            ).first()

            if existing_feedback:
                return error_response("Feedback already submitted for this event", 409)

            # Create feedback
            feedback = Feedback()
            feedback.event_id = event_uuid
            feedback.student_id = current_user.id
            feedback.rating = payload.rating
            feedback.comment = payload.comment
            feedback.aspects = payload.aspects

            db.session.add(feedback)
            db.session.commit()

            return success_response(
                "Feedback submitted successfully",
                201,
                feedback.to_dict()
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to submit feedback: {str(e)}", 500)

    @staticmethod
    def update_feedback(event_id: str):
        """Update existing feedback for an event (Participant only)."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Validate request data using Pydantic schema
            payload = UpdateFeedbackRequest.model_validate(request.get_json())

            # Find existing feedback
            feedback = Feedback.query.filter_by(
                event_id=event_uuid,
                student_id=current_user.id
            ).first()

            if not feedback:
                return error_response("Feedback not found for this event", 404)

            # Update fields
            if payload.rating is not None:
                feedback.rating = payload.rating
            if payload.comment is not None:
                feedback.comment = payload.comment
            if payload.aspects is not None:
                feedback.aspects = payload.aspects

            db.session.commit()

            return success_response(
                "Feedback updated successfully",
                200,
                feedback.to_dict()
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update feedback: {str(e)}", 500)

    @staticmethod
    def get_user_feedback():
        """Get current user's feedback (Participant only)."""
        try:
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))

            # Get feedback
            feedback = Feedback.query.filter_by(
                student_id=current_user.id
            ).order_by(Feedback.submitted_on.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(
                "User feedback retrieved successfully",
                200,
                {
                    'feedback': [f.to_dict() for f in feedback.items],
                    'pagination': {
                        'page': feedback.page,
                        'per_page': feedback.per_page,
                        'total': feedback.total,
                        'pages': feedback.pages,
                        'has_next': feedback.has_next,
                        'has_prev': feedback.has_prev
                    }
                }
            )

        except Exception as e:
            return error_response(f"Failed to retrieve feedback: {str(e)}", 500)

    @staticmethod
    def delete_feedback(event_id: str):
        """Delete feedback for an event (Participant only)."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Find feedback
            feedback = Feedback.query.filter_by(
                event_id=event_uuid,
                student_id=current_user.id
            ).first()

            if not feedback:
                return error_response("Feedback not found for this event", 404)

            db.session.delete(feedback)
            db.session.commit()

            return success_response("Feedback deleted successfully", 200)

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete feedback: {str(e)}", 500)

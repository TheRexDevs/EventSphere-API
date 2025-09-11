"""
Admin Feedback Controller

Handles feedback management and analytics for administrators and organizers.

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
from app.utils.helpers.http_response import success_response, error_response


class AdminFeedbackController:
    """Controller for admin feedback operations."""

    @staticmethod
    def get_event_feedback(event_id: str):
        """Get all feedback for a specific event (Admin/Organizer only)."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Verify event exists
            event = Event.query.get(event_uuid)
            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            if (event.organizer_id != current_user.id and
                current_user.role != 'admin'):
                return error_response("Insufficient permissions", 403)

            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            rating_filter = request.args.get('rating')  # Filter by rating

            # Build query
            query = Feedback.query.filter_by(event_id=event_uuid)

            if rating_filter:
                query = query.filter_by(rating=int(rating_filter))

            # Get feedback
            feedback = query.order_by(Feedback.submitted_on.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Calculate statistics
            all_feedback = Feedback.query.filter_by(event_id=event_uuid).all()
            total_feedback = len(all_feedback)
            average_rating = sum(f.rating for f in all_feedback) / total_feedback if total_feedback > 0 else 0

            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = len([f for f in all_feedback if f.rating == i])

            # Aspects summary
            aspects_summary = {}
            for feedback_item in all_feedback:
                if feedback_item.aspects:
                    for aspect, rating in feedback_item.aspects.items():
                        if aspect not in aspects_summary:
                            aspects_summary[aspect] = {'total': 0, 'count': 0, 'average': 0}
                        aspects_summary[aspect]['total'] += rating
                        aspects_summary[aspect]['count'] += 1

            # Calculate averages
            for aspect_data in aspects_summary.values():
                if aspect_data['count'] > 0:
                    aspect_data['average'] = round(aspect_data['total'] / aspect_data['count'], 1)

            return success_response(
                "Event feedback retrieved successfully",
                200,
                {
                    'event': {
                        'id': str(event.id),
                        'title': event.title,
                        'date': event.date.isoformat() if event.date else None
                    },
                    'feedback': [f.to_dict() for f in feedback.items],
                    'pagination': {
                        'page': feedback.page,
                        'per_page': feedback.per_page,
                        'total': feedback.total,
                        'pages': feedback.pages,
                        'has_next': feedback.has_next,
                        'has_prev': feedback.has_prev
                    },
                    'summary': {
                        'total_feedback': total_feedback,
                        'average_rating': round(average_rating, 1),
                        'rating_distribution': rating_distribution,
                        'aspects_summary': aspects_summary
                    }
                }
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            return error_response(f"Failed to retrieve feedback: {str(e)}", 500)

    @staticmethod
    def get_feedback_stats():
        """Get overall feedback statistics (Admin only)."""
        try:
            current_user = g.user

            if not current_user or current_user.role != 'admin':
                return error_response("Admin access required", 403)

            # Get query parameters
            event_id = request.args.get('event_id')
            days = int(request.args.get('days', 30))  # Last N days

            # Build query
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = Feedback.query.filter(Feedback.submitted_on >= cutoff_date)

            if event_id:
                query = query.filter_by(event_id=uuid.UUID(event_id))

            # Get feedback
            all_feedback = query.all()
            total_feedback = len(all_feedback)

            if total_feedback == 0:
                return success_response(
                    "No feedback found in the specified period",
                    200,
                    {
                        'total_feedback': 0,
                        'average_rating': 0,
                        'rating_distribution': {i: 0 for i in range(1, 6)},
                        'aspects_summary': {},
                        'recent_feedback': []
                    }
                )

            # Calculate statistics
            average_rating = sum(f.rating for f in all_feedback) / total_feedback

            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = len([f for f in all_feedback if f.rating == i])

            # Aspects summary
            aspects_summary = {}
            for feedback_item in all_feedback:
                if feedback_item.aspects:
                    for aspect, rating in feedback_item.aspects.items():
                        if aspect not in aspects_summary:
                            aspects_summary[aspect] = {'total': 0, 'count': 0, 'average': 0}
                        aspects_summary[aspect]['total'] += rating
                        aspects_summary[aspect]['count'] += 1

            # Calculate averages
            for aspect_data in aspects_summary.values():
                if aspect_data['count'] > 0:
                    aspect_data['average'] = round(aspect_data['total'] / aspect_data['count'], 1)

            # Recent feedback (last 10)
            recent_feedback = all_feedback[-10:] if len(all_feedback) > 10 else all_feedback

            return success_response(
                "Feedback statistics retrieved successfully",
                200,
                {
                    'total_feedback': total_feedback,
                    'average_rating': round(average_rating, 1),
                    'rating_distribution': rating_distribution,
                    'aspects_summary': aspects_summary,
                    'recent_feedback': [f.to_dict() for f in recent_feedback],
                    'period_days': days
                }
            )

        except Exception as e:
            return error_response(f"Failed to retrieve feedback statistics: {str(e)}", 500)

"""
Admin Feedback Routes

Handles feedback viewing and analytics for administrators and organizers.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import AdminFeedbackController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.feedback import FeedbackListResponse, FeedbackStatsResponse

def register_routes(bp):
    """Register admin feedback routes."""

    @bp.get("/events/<string:event_id>/feedback")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Feedback Management"],
        summary="Get Event Feedback",
        description="Get all feedback and statistics for a specific event (Admin/Organizer only)",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
            QueryParameter("rating", "integer", required=False, description="Filter by rating (1-5)"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def get_event_feedback(event_id: str):
        """Get feedback for an event."""
        return AdminFeedbackController.get_event_feedback(event_id)

    @bp.get("/feedback/stats")
    @roles_required('admin')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Feedback Management"],
        summary="Get Feedback Statistics",
        description="Get overall feedback statistics across all events (Admin only)",
        query_params=[
            QueryParameter("event_id", "string", required=False, description="Filter by specific event ID"),
            QueryParameter("days", "integer", required=False, description="Number of days to look back", default=30),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def get_feedback_stats():
        """Get feedback statistics."""
        return AdminFeedbackController.get_feedback_stats()

"""
Public Feedback Routes

Handles feedback submission and viewing for authenticated participants.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import PublicFeedbackController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.feedback import SubmitFeedbackRequest, UpdateFeedbackRequest, FeedbackListResponse

def register_routes(bp):
    """Register public feedback routes."""

    @bp.post("/events/<string:event_id>/feedback")
    @roles_required('participant')
    @endpoint(
        request_body=SubmitFeedbackRequest,
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Feedback"],
        summary="Submit Feedback",
        description="Submit feedback and rating for an event (Participant only)"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse, HTTP_409=ApiResponse))
    def submit_feedback(event_id: str):
        """Submit feedback for an event."""
        return PublicFeedbackController.submit_feedback(event_id)

    @bp.put("/events/<string:event_id>/feedback")
    @roles_required('participant')
    @endpoint(
        request_body=UpdateFeedbackRequest,
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Feedback"],
        summary="Update Feedback",
        description="Update existing feedback for an event (Participant only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def update_feedback(event_id: str):
        """Update feedback for an event."""
        return PublicFeedbackController.update_feedback(event_id)

    @bp.delete("/events/<string:event_id>/feedback")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Feedback"],
        summary="Delete Feedback",
        description="Delete feedback for an event (Participant only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def delete_feedback(event_id: str):
        """Delete feedback for an event."""
        return PublicFeedbackController.delete_feedback(event_id)

    @bp.get("/feedback")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Feedback"],
        summary="Get User Feedback",
        description="Get paginated list of user's submitted feedback (Participant only)",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse))
    def get_user_feedback():
        """Get user's feedback."""
        return PublicFeedbackController.get_user_feedback()

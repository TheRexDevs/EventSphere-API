"""
Public Event Routes

Defines public event browsing endpoints accessible to all users
without authentication requirements.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import PublicEventController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter
from app.schemas.event import EventResponse, EventListResponse, EventCategoriesResponse
from app.schemas.common import ApiResponse

def register_routes(bp):
    """Register public event routes."""

    @bp.get("/events")
    @endpoint(
        tags=["Public Events"],
        summary="Browse Events",
        description="Get list of approved events with basic filtering",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
            QueryParameter("search", "string", required=False, description="Search in title, description, venue"),
            QueryParameter("category", "string", required=False, description="Filter by category name"),
            QueryParameter("venue", "string", required=False, description="Filter by venue"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse))
    def get_events():
        """Get public events."""
        return PublicEventController.get_events()

    @bp.get("/events/<string:event_id>")
    @endpoint(
        tags=["Public Events"],
        summary="Get Event Details",
        description="Get detailed information about a specific approved event"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_404=ApiResponse))
    def get_event(event_id: str):
        """Get a specific event."""
        return PublicEventController.get_event(event_id)

    @bp.get("/events/categories")
    @endpoint(
        tags=["Public Events"],
        summary="Get Event Categories",
        description="Get all available event categories"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse))
    def get_event_categories():
        """Get event categories."""
        return PublicEventController.get_event_categories()

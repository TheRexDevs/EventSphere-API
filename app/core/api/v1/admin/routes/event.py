"""
Event Management Routes for Admin API

Defines all event-related endpoints for administrators and organizers
including CRUD operations, approval workflow, and event management.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import EventController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.event import (
    CreateEventRequest,
    UpdateEventRequest,
    CreateEventWithFilesRequest,
    UpdateEventWithFilesRequest,
    EventResponse,
    EventListResponse,
    EventCategoriesResponse,
    ApproveEventRequest,
    PublishEventRequest
)

def register_routes(bp):
    """Register event management routes."""

    # Event CRUD Operations
    @bp.post("/events")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=CreateEventRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="Create Event",
        description="Create a new event (Organizer/Admin only)"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def create_event():
        """Create a new event."""
        return EventController.create_event()

    @bp.get("/events")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="List Events",
        description="Get paginated list of all events with filtering",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
            QueryParameter("status", "string", required=False, description="Filter by status (pending, approved, cancelled)"),
            QueryParameter("organizer_id", "string", required=False, description="Filter by organizer ID"),
            QueryParameter("search", "string", required=False, description="Search in title, description, venue"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse))
    def get_events():
        """Get all events."""
        return EventController.get_events()

    @bp.get("/events/<string:event_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="Get Event Details",
        description="Get detailed information about a specific event"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def get_event(event_id: str):
        """Get a specific event."""
        return EventController.get_event(event_id)

    @bp.put("/events/<string:event_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=UpdateEventRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="Update Event",
        description="Update an existing event (Organizer/Admin only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def update_event(event_id: str):
        """Update an event."""
        return EventController.update_event(event_id)

    @bp.delete("/events/<string:event_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="Delete Event",
        description="Delete an event (Organizer/Admin only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def delete_event(event_id: str):
        """Delete an event."""
        return EventController.delete_event(event_id)

    # Event Approval and Publishing
    @bp.post("/events/<string:event_id>/approve")
    @roles_required('admin')
    @endpoint(
        request_body=ApproveEventRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="Approve Event",
        description="Approve a pending event (Admin only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def approve_event(event_id: str):
        """Approve an event."""
        return EventController.approve_event(event_id)

    @bp.post("/events/<string:event_id>/publish")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=PublishEventRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Event Management"],
        summary="Publish/Unpublish Event",
        description="Toggle publish status of an approved event (Organizer/Admin only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def publish_event(event_id: str):
        """Publish/unpublish an event."""
        return EventController.publish_event(event_id)

"""
Registration Routes

Handles event registration endpoints for participants,
including registration, cancellation, and management.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import RegistrationController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.registration import (
    RegisterForEventRequest,
    CancelRegistrationRequest,
    RegistrationResponse,
    RegistrationListResponse
)

def register_routes(bp):
    """Register registration routes."""

    @bp.post("/events/<string:event_id>/register")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Event Registration"],
        summary="Register for Event",
        description="Register the authenticated user for an approved event"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse, HTTP_409=ApiResponse))
    def register_for_event(event_id: str):
        """Register for an event."""
        return RegistrationController.register_for_event(event_id)

    @bp.delete("/events/<string:event_id>/register")
    @roles_required('participant')
    @endpoint(
        request_body=CancelRegistrationRequest,
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Event Registration"],
        summary="Cancel Registration",
        description="Cancel registration for an event"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def cancel_registration(event_id: str):
        """Cancel event registration."""
        return RegistrationController.cancel_registration(event_id)

    @bp.get("/registrations")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Event Registration"],
        summary="Get User Registrations",
        description="Get paginated list of user's event registrations",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
            QueryParameter("status", "string", required=False, description="Filter by status (confirmed, cancelled)", default="confirmed"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse))
    def get_user_registrations():
        """Get user's registrations."""
        return RegistrationController.get_user_registrations()

    @bp.get("/registrations/<string:registration_id>")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Event Registration"],
        summary="Get Registration Details",
        description="Get details of a specific registration"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def get_registration_details(registration_id: str):
        """Get registration details."""
        return RegistrationController.get_registration_details(registration_id)

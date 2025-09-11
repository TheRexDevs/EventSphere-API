"""
Attendance Routes

Handles attendance marking and tracking for events.
Provides admin/organizer access to attendance management.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import AttendanceController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse

def register_routes(bp):
    """Register attendance routes."""

    @bp.post("/attendance")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Attendance Management"],
        summary="Mark Attendance",
        description="Mark attendance for a participant (Admin/Organizer only)"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse, HTTP_409=ApiResponse))
    def mark_attendance():
        """Mark attendance for a participant."""
        return AttendanceController.mark_attendance()

    @bp.get("/attendance/<string:event_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Attendance Management"],
        summary="Get Event Attendance",
        description="Get attendance list and statistics for an event (Admin/Organizer only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def get_event_attendance(event_id: str):
        """Get attendance for an event."""
        return AttendanceController.get_event_attendance(event_id)

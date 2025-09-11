"""
Certificate Routes for Admin API

Handles certificate generation and management for administrators and organizers.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import CertificateController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.certificate import GenerateCertificateRequest, BulkGenerateCertificatesRequest

def register_routes(bp):
    """Register certificate routes."""

    @bp.post("/certificates")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=GenerateCertificateRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Certificate Management"],
        summary="Generate Certificate",
        description="Generate certificate for specific participants (Admin/Organizer only)"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def generate_certificate():
        """Generate certificate for participants."""
        return CertificateController.generate_certificate()

    @bp.post("/certificates/bulk")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=BulkGenerateCertificatesRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Certificate Management"],
        summary="Bulk Generate Certificates",
        description="Generate certificates for all attendees or specific participants (Admin/Organizer only)"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def bulk_generate_certificates():
        """Bulk generate certificates."""
        return CertificateController.bulk_generate_certificates()

    @bp.get("/events/<string:event_id>/certificates")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Certificate Management"],
        summary="Get Event Certificates",
        description="Get all certificates for a specific event (Admin/Organizer only)",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def get_event_certificates(event_id: str):
        """Get certificates for an event."""
        return CertificateController.get_event_certificates(event_id)

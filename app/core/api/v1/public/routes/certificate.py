"""
Public Certificate Routes

Handles certificate download and viewing for authenticated participants.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import PublicCertificateController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.certificate import DownloadCertificateRequest

def register_routes(bp):
    """Register public certificate routes."""

    @bp.get("/certificates/<string:certificate_id>/download")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Certificate Access"],
        summary="Download Certificate",
        description="Download certificate PDF file (Participant only)"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def download_certificate(certificate_id: str):
        """Download certificate."""
        return PublicCertificateController.download_certificate(certificate_id)

    @bp.get("/certificates")
    @roles_required('participant')
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Certificate Access"],
        summary="Get User Certificates",
        description="Get paginated list of user's certificates (Participant only)",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse))
    def get_user_certificates():
        """Get user's certificates."""
        return PublicCertificateController.get_user_certificates()

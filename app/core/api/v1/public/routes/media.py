"""
Public media access routes for the public API.

This module defines public media access endpoints for viewing media
without authentication requirements.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import MediaController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter
from app.schemas.common import ApiResponse

def register_routes(bp):
    # Public Media Access (No Authentication Required)

    @bp.get("/events/public/<string:handle>/media")
    @endpoint(
        tags=["Public Access"],
        summary="Get Public Media",
        description="Get media files for a public event by handle",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number for pagination", default=1),
            QueryParameter("per_page", "integer", required=False, description="Number of items per page (max 50)", default=20),
            QueryParameter("file_type", "string", required=False, description="Filter by file type (image, video, document)"),
            QueryParameter("is_featured", "boolean", required=False, description="Show only featured media"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_404=ApiResponse))
    def get_public_media(handle: str):
        """Get public media for a published event."""
        return MediaController.get_public_media(handle)

"""
Media management routes for the public API.

This module defines all media-related endpoints including upload, listing,
deletion, statistics, and public media access.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import MediaController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, SecurityScheme, QueryParameter
from app.schemas.common import ApiResponse
from app.schemas.media import (
    UploadMediaRequest,
    DeleteMediaRequest,
    UpdateMediaRequest,
    MediaResponse,
    MediaListResponse,
    MediaStatsResponse,
    BulkDeleteResponse,
)

def register_routes(bp):
    # Media Management Endpoints (Authenticated)

    @bp.post("/events/<string:event_id>/media/upload")
    @endpoint(
        request_body=UploadMediaRequest,
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="Upload Media Files",
        description="Upload media files (images, videos, documents) to a event with automatic optimization"
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def upload_media(event_id: str):
        """Upload media files to a event."""
        return MediaController.upload_media(event_id)


    @bp.get("/events/<string:event_id>/media")
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="List Folio Media",
        description="Get paginated list of all media files within a event",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number for pagination", default=1),
            QueryParameter("per_page", "integer", required=False, description="Number of items per page (max 50)", default=20),
            QueryParameter("file_type", "string", required=False, description="Filter by file type (image, video, document)"),
            QueryParameter("is_featured", "boolean", required=False, description="Filter by featured media only"),
            QueryParameter("search", "string", required=False, description="Search in filenames"),
            QueryParameter("sort", "string", required=False, description="Sort order (created_at, filename, file_size)", default="created_at"),
            QueryParameter("order", "string", required=False, description="Sort direction (asc, desc)", default="desc"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def list_media(event_id: str):
        """List all media within a event."""
        return MediaController.list_media(event_id)


    @bp.get("/events/<string:event_id>/media/<string:media_id>")
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="Get Media Details",
        description="Get detailed information about a specific media file"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def get_media(event_id: str, media_id: str):
        """Get a specific media file by ID."""
        return MediaController.get_media(event_id, media_id)


    @bp.put("/events/<string:event_id>/media/<string:media_id>")
    @endpoint(
        request_body=UpdateMediaRequest,
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="Update Media Metadata",
        description="Update media file metadata including filename and featured status"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def update_media(event_id: str, media_id: str):
        """Update media metadata."""
        return MediaController.update_media(event_id, media_id)


    @bp.delete("/events/<string:event_id>/media/<string:media_id>")
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="Delete Media File",
        description="Permanently delete a media file and all its optimized versions"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def delete_media(event_id: str, media_id: str):
        """Delete a specific media file."""
        return MediaController.delete_media(event_id, media_id)


    @bp.post("/events/<string:event_id>/media/bulk-delete")
    @endpoint(
        request_body=DeleteMediaRequest,
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="Bulk Delete Media Files",
        description="Delete multiple media files in a single request"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def bulk_delete_media(event_id: str):
        """Delete multiple media files."""
        return MediaController.bulk_delete_media(event_id)


    # Media Analytics Endpoints

    @bp.get("/events/<string:event_id>/media/stats")
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Media Library"],
        summary="Get Media Statistics",
        description="Get usage statistics and analytics for media within a event",
        query_params=[
            QueryParameter("period", "string", required=False, description="Time period for stats (day, week, month, year)", default="month"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def get_media_stats(event_id: str):
        """Get media statistics for a event."""
        return MediaController.get_media_stats(event_id)


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

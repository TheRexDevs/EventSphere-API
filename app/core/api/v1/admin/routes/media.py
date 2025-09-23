"""
Admin media management routes for the admin API.

This module defines all admin media-related endpoints including upload, listing,
deletion, statistics, and media access for admins and organizers.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import AdminMediaController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, SecurityScheme, QueryParameter
from app.utils.decorators.auth import roles_required
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
    # Admin Media Management Endpoints

    @bp.post("/events/<string:event_id>/media/upload")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=UploadMediaRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="Upload Media Files",
        description="Upload media files (images, videos, documents) to an event with automatic optimization. Requires admin or organizer role."
    )
    @spec.validate(resp=Response(HTTP_201=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def upload_media(event_id: str):
        """Upload media files to an event."""
        return AdminMediaController.upload_media(event_id)


    @bp.get("/events/<string:event_id>/media")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="List Event Media",
        description="Get paginated list of all media files within an event. Requires admin or organizer role.",
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
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def list_media(event_id: str):
        """List all media within an event."""
        return AdminMediaController.list_media(event_id)


    @bp.get("/events/<string:event_id>/media/<string:media_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="Get Media Details",
        description="Get detailed information about a specific media file. Requires admin or organizer role."
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def get_media(event_id: str, media_id: str):
        """Get a specific media file by ID."""
        return AdminMediaController.get_media(event_id, media_id)


    @bp.put("/events/<string:event_id>/media/<string:media_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=UpdateMediaRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="Update Media Metadata",
        description="Update media file metadata including filename and featured status. Requires admin or organizer role."
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def update_media(event_id: str, media_id: str):
        """Update media metadata."""
        return AdminMediaController.update_media(event_id, media_id)


    @bp.delete("/events/<string:event_id>/media/<string:media_id>")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="Delete Media File",
        description="Permanently delete a media file and all its optimized versions. Requires admin or organizer role."
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def delete_media(event_id: str, media_id: str):
        """Delete a specific media file."""
        return AdminMediaController.delete_media(event_id, media_id)


    @bp.post("/events/<string:event_id>/media/bulk-delete")
    @roles_required('admin', 'organizer')
    @endpoint(
        request_body=DeleteMediaRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="Bulk Delete Media Files",
        description="Delete multiple media files in a single request. Requires admin or organizer role."
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def bulk_delete_media(event_id: str):
        """Delete multiple media files."""
        return AdminMediaController.bulk_delete_media(event_id)


    # Admin Media Analytics Endpoints

    @bp.get("/events/<string:event_id>/media/stats")
    @roles_required('admin', 'organizer')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["Admin Media Library"],
        summary="Get Media Statistics",
        description="Get usage statistics and analytics for media within an event. Requires admin or organizer role.",
        query_params=[
            QueryParameter("period", "string", required=False, description="Time period for stats (day, week, month, year)", default="month"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse, HTTP_404=ApiResponse))
    def get_media_stats(event_id: str):
        """Get media statistics for an event."""
        return AdminMediaController.get_media_stats(event_id)

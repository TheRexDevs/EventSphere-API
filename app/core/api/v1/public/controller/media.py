"""
Media controller for managing file uploads and media library within folios.

This module handles all media-related operations including upload, deletion,
gallery management, and search with proper folio ownership validation.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: Folio Builder
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, asc, desc
from flask_sqlalchemy.pagination import Pagination
import uuid

from app.extensions import db
from app.logging import log_error, log_event
from app.models import Media, Folio
from app.schemas.media import (
    UploadMediaRequest,
    DeleteMediaRequest,
    UpdateMediaRequest,
    MediaResponse,
    MediaListResponse,
    MediaStatsResponse,
    MediaUploadResponse,
    BulkDeleteResponse,
)
from app.utils.helpers.http_response import success_response, error_response
from app.utils.media_service import MediaService


class MediaController:
    """Controller for media management operations within folios."""

    @staticmethod
    def _validate_media_uuid(media_id: str) -> Optional[uuid.UUID]:
        """Validate and convert media ID string to UUID."""
        try:
            return uuid.UUID(media_id)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _validate_folio_uuid(folio_id: str) -> Optional[uuid.UUID]:
        """Validate and convert folio ID string to UUID."""
        try:
            return uuid.UUID(folio_id)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _validate_user_uuid(user_id: str) -> Optional[uuid.UUID]:
        """Validate and convert user ID string to UUID."""
        try:
            return uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_user_folio(folio_id: str, user_id: str) -> Tuple[Optional[Response], Optional[Folio]]:
        """Get folio by ID and verify ownership. Returns (error_response, folio) tuple."""
        # Validate UUID formats
        folio_uuid = MediaController._validate_folio_uuid(folio_id)
        if not folio_uuid:
            return error_response("invalid folio ID format", 400), None

        user_uuid = MediaController._validate_user_uuid(user_id)
        if not user_uuid:
            return error_response("invalid user ID format", 401), None

        # Get folio and verify ownership
        folio = Folio.query.filter_by(id=folio_uuid, owner_id=user_uuid).first()
        if not folio:
            return error_response("folio not found or access denied", 404), None

        return None, folio

    @staticmethod
    def _get_folio_media(folio_id: str, media_id: str, user_id: str) -> Tuple[Optional[Response], Optional[Media], Optional[Folio]]:
        """Get media by ID, verify folio ownership. Returns (error_response, media, folio) tuple."""
        # First validate folio ownership
        error_resp, folio = MediaController._get_user_folio(folio_id, user_id)
        if error_resp:
            return error_resp, None, None

        # Validate media UUID
        media_uuid = MediaController._validate_media_uuid(media_id)
        if not media_uuid:
            return error_response("invalid media ID format", 400), None, folio

        # Get media within the folio
        if folio is None:
            return error_response("folio access denied", 403), None, None

        media = Media.query.filter_by(id=media_uuid, folio_id=folio.id).first()
        if not media:
            return error_response("media not found", 404), None, folio

        return None, media, folio

    @staticmethod
    @jwt_required()
    def upload_media(folio_id: str) -> Response:
        """Upload media files to a folio."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Validate folio ownership
        error_resp, folio = MediaController._get_user_folio(folio_id, user_id)
        if error_resp:
            return error_resp

        if folio is None:
            return error_response("folio access denied", 403)

        try:
            # Check if files are provided
            if 'files' not in request.files:
                return error_response("no files provided", 400)

            files = request.files.getlist('files')
            if not files or len(files) == 0:
                return error_response("no files provided", 400)

            # Parse upload options
            payload = UploadMediaRequest.model_validate(request.form)

            uploaded_media = []
            errors = []

            for file in files:
                if file.filename == '':
                    continue

                try:
                    # Upload using enhanced service
                    media = MediaService.upload_media_file(
                        file=file,
                        folio_id=folio.id,
                        custom_filename=payload.custom_filename,
                        optimization=payload.optimize
                    )
                    uploaded_media.append(media)

                except Exception as e:
                    log_error(f"Failed to upload {file.filename}", e)
                    errors.append(f"Failed to upload {file.filename}: {str(e)}")

            if not uploaded_media:
                return error_response("no files were uploaded successfully", 400)

            # Return response
            response_data = {
                "uploaded": [MediaResponse.model_validate(media.to_dict()).model_dump() for media in uploaded_media],
                "errors": errors,
                "message": f"Successfully uploaded {len(uploaded_media)} file(s)"
            }

            log_event(f"Media uploaded to folio {folio.handle}", data={
                "folio_id": str(folio.id),
                "user_id": str(user_id),
                "uploaded_count": len(uploaded_media),
                "error_count": len(errors)
            })

            return success_response(
                f"Successfully uploaded {len(uploaded_media)} file(s)",
                201,
                response_data
            )

        except Exception as e:
            log_error(f"Media upload failed: {str(e)}", error=e)
            return error_response("upload failed", 500)

    @staticmethod
    @jwt_required()
    def list_media(folio_id: str) -> Response:
        """List all media within a folio."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Validate folio ownership
        error_resp, folio = MediaController._get_user_folio(folio_id, user_id)
        if error_resp:
            return error_resp

        if folio is None:
            return error_response("folio access denied", 403)

        # Get pagination and filtering parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)  # Max 50 per page
        file_type = request.args.get('file_type')
        is_featured = request.args.get('is_featured', type=bool)
        search = request.args.get('search', '').strip()
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        # Build query
        stmt = select(Media).where(Media.folio_id == folio.id)

        # Apply filters
        if file_type:
            stmt = stmt.where(Media.file_type == file_type)

        if is_featured is not None:
            stmt = stmt.where(Media.is_featured == is_featured)

        if search:
            stmt = stmt.where(
                (Media.filename.ilike(f'%{search}%')) |
                (Media.original_filename.ilike(f'%{search}%'))
            )

        # Apply sorting
        sort_column = getattr(Media, sort, Media.created_at)
        if order.lower() == 'desc':
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))

        # Paginate
        paginated: Pagination = db.paginate(
            stmt,
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Convert to response format
        media_responses = [
            MediaResponse.model_validate(media.to_dict())
            for media in paginated.items
        ]

        response_data = MediaListResponse(
            media=media_responses,
            total=paginated.total or 0,
            page=page,
            per_page=per_page,
            has_next=paginated.has_next,
            has_prev=paginated.has_prev
        )

        return success_response("Media retrieved successfully", 200, response_data.model_dump())

    @staticmethod
    @jwt_required()
    def get_media(folio_id: str, media_id: str) -> Response:
        """Get a specific media file by ID."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Get media and validate ownership
        error_resp, media, folio = MediaController._get_folio_media(folio_id, media_id, user_id)
        if error_resp:
            return error_resp

        if media is None:
            return error_response("media not found", 404)

        if folio is None:
            return error_response("folio access denied", 403)

        # Increment usage count
        media.increment_usage()

        return success_response(
            "Media retrieved successfully",
            200,
            {"media": MediaResponse.model_validate(media.to_dict()).model_dump()}
        )

    @staticmethod
    @jwt_required()
    def update_media(folio_id: str, media_id: str) -> Response:
        """Update media metadata."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Get media and validate ownership
        error_resp, media, folio = MediaController._get_folio_media(folio_id, media_id, user_id)
        if error_resp:
            return error_resp

        if media is None:
            return error_response("media not found", 404)

        if folio is None:
            return error_response("folio access denied", 403)

        # Parse request
        payload = UpdateMediaRequest.model_validate(request.get_json())

        try:
            # Update fields
            if payload.filename is not None:
                media.filename = payload.filename
            if payload.is_featured is not None:
                media.is_featured = payload.is_featured

            media.updated_at = db.func.now()
            db.session.commit()

            log_event(f"Media updated: {media.filename}", data={
                "media_id": str(media.id),
                "folio_id": str(folio.id),
                "user_id": str(user_id)
            })

            return success_response(
                "Media updated successfully",
                200,
                {"media": MediaResponse.model_validate(media.to_dict()).model_dump()}
            )

        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to update media: {str(e)}", error=e)
            return error_response("failed to update media", 500)

    @staticmethod
    @jwt_required()
    def delete_media(folio_id: str, media_id: str) -> Response:
        """Delete a specific media file."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Get media and validate ownership
        error_resp, media, folio = MediaController._get_folio_media(folio_id, media_id, user_id)
        if error_resp:
            return error_resp

        if media is None:
            return error_response("media not found", 404)

        if folio is None:
            return error_response("folio access denied", 403)

        try:
            filename = media.filename
            success = MediaService.delete_media(media.id, folio.id)

            if success:
                log_event(f"Media deleted: {filename}", data={
                    "media_id": str(media_id),
                    "folio_id": str(folio.id),
                    "user_id": str(user_id)
                })

                return success_response("Media deleted successfully", 200)
            else:
                return error_response("failed to delete media", 500)

        except Exception as e:
            log_error(f"Failed to delete media: {str(e)}", error=e)
            return error_response("failed to delete media", 500)

    @staticmethod
    @jwt_required()
    def get_media_stats(folio_id: str) -> Response:
        """Get media statistics for a folio."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Validate folio ownership
        error_resp, folio = MediaController._get_user_folio(folio_id, user_id)
        if error_resp:
            return error_resp

        if folio is None:
            return error_response("folio access denied", 403)

        try:
            stats = MediaService.get_media_usage_stats(folio.id)

            response_data = MediaStatsResponse(
                total_files=stats.get('total_files', 0),
                total_size=stats.get('total_size', 0),
                total_size_mb=stats.get('total_size', 0) / (1024 * 1024),
                by_type=stats.get('by_type', {})
            )

            return success_response("Media statistics retrieved successfully", 200, response_data.model_dump())

        except Exception as e:
            log_error(f"Failed to get media stats: {str(e)}", error=e)
            return error_response("failed to retrieve media statistics", 500)

    @staticmethod
    @jwt_required()
    def bulk_delete_media(folio_id: str) -> Response:
        """Delete multiple media files."""
        current_user_id = get_jwt_identity()

        if not current_user_id or not isinstance(current_user_id, dict):
            return error_response("invalid token format", 401)

        user_id = current_user_id.get("user_id")
        if not user_id:
            return error_response("invalid token claims", 401)

        # Validate folio ownership
        error_resp, folio = MediaController._get_user_folio(folio_id, user_id)
        if error_resp:
            return error_resp

        if folio is None:
            return error_response("folio access denied", 403)

        # Parse request
        payload = DeleteMediaRequest.model_validate(request.get_json())

        try:
            deleted_count = 0
            failed_deletions = []

            for media_id in payload.media_ids:
                success = MediaService.delete_media(media_id, folio.id)
                if success:
                    deleted_count += 1
                else:
                    failed_deletions.append(str(media_id))

            log_event(f"Bulk media deletion in folio {folio.handle}", data={
                "folio_id": str(folio.id),
                "user_id": str(user_id),
                "deleted_count": deleted_count,
                "failed_count": len(failed_deletions)
            })

            response_data = BulkDeleteResponse(
                deleted_count=deleted_count,
                failed_deletions=failed_deletions,
                message=f"Successfully deleted {deleted_count} file(s)"
            )

            return success_response(
                f"Successfully deleted {deleted_count} file(s)",
                200,
                response_data.model_dump()
            )

        except Exception as e:
            log_error(f"Failed to bulk delete media: {str(e)}", error=e)
            return error_response("failed to delete media", 500)

    # Public Access Methods (No Authentication)

    @staticmethod
    def get_public_media(handle: str) -> Response:
        """Get public media for a published folio by handle."""
        # Get folio by handle
        folio = Folio.query.filter_by(handle=handle, is_published=True).first()
        if not folio:
            return error_response("folio not found", 404)

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)  # Max 50 per page for public
        file_type = request.args.get('file_type')
        is_featured = request.args.get('is_featured', type=bool)

        # Build query for public media only
        stmt = select(Media).where(Media.folio_id == folio.id)

        if file_type:
            stmt = stmt.where(Media.file_type == file_type)

        if is_featured:
            stmt = stmt.where(Media.is_featured == True)

        stmt = stmt.order_by(desc(Media.created_at))

        # Paginate
        paginated: Pagination = db.paginate(
            stmt,
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Convert to response format
        media_responses = [
            MediaResponse.model_validate(media.to_dict())
            for media in paginated.items
        ]

        response_data = MediaListResponse(
            media=media_responses,
            total=paginated.total or 0,
            page=page,
            per_page=per_page,
            has_next=paginated.has_next,
            has_prev=paginated.has_prev
        )

        return success_response("Media retrieved successfully", 200, response_data.model_dump())

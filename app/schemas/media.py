"""
Pydantic schemas for Media file management.

This module defines request and response schemas for media-related API operations
including upload, listing, deletion, and metadata retrieval.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class UploadMediaRequest(BaseModel):
    """Request schema for uploading media files."""

    custom_filename: Optional[str] = Field(None, min_length=1, max_length=200, description="Optional custom filename")
    optimize: bool = Field(True, description="Whether to apply image optimizations")

    @field_validator('custom_filename')
    def validate_custom_filename(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Basic validation for filename
            import re
            if not re.match(r'^[a-zA-Z0-9\-_\.\s]+$', v):
                raise ValueError('Custom filename contains invalid characters')
            # Remove path separators for security
            if '/' in v or '\\' in v:
                raise ValueError('Custom filename cannot contain path separators')
        return v


class DeleteMediaRequest(BaseModel):
    """Request schema for deleting media files."""

    media_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=50, description="List of media IDs to delete")


class UpdateMediaRequest(BaseModel):
    """Request schema for updating media metadata."""

    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    is_featured: Optional[bool] = Field(None)

    @field_validator('filename')
    def validate_filename(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from werkzeug.utils import secure_filename
            v = secure_filename(v)
            if not v:
                raise ValueError('Invalid filename')
        return v


class MediaResponse(BaseModel):
    """Response schema for a single media file."""

    id: uuid.UUID
    folio_id: uuid.UUID
    filename: str
    original_filename: str
    file_path: str
    file_url: str
    thumbnail_url: Optional[str]
    file_size: int
    file_type: str
    mime_type: str
    file_extension: str
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    cloudinary_public_id: str
    cloudinary_folder: str
    optimized_versions: Dict[str, str]
    is_featured: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MediaListResponse(BaseModel):
    """Response schema for paginated media list."""

    media: List[MediaResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

    model_config = {"from_attributes": True}


class MediaStatsResponse(BaseModel):
    """Response schema for media statistics."""

    total_files: int
    total_size: int
    total_size_mb: float
    by_type: Dict[str, Dict[str, Any]]

    model_config = {"from_attributes": True}


class MediaUploadResponse(BaseModel):
    """Response schema for successful media upload."""

    media: MediaResponse
    message: str = "Media uploaded successfully"

    model_config = {"from_attributes": True}


class BulkDeleteResponse(BaseModel):
    """Response schema for bulk media deletion."""

    deleted_count: int
    failed_deletions: List[str]
    message: str

    model_config = {"from_attributes": True}

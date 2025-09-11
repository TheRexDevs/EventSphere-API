"""
Pydantic schemas for Certificate management.

This module defines request and response schemas for certificate-related API operations
including generation, download, and management.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class GenerateCertificateRequest(BaseModel):
    """Request schema for generating certificates."""

    event_id: uuid.UUID = Field(..., description="UUID of the event")
    student_ids: List[uuid.UUID] = Field(..., min_length=1, description="List of student IDs to generate certificates for")
    template_type: Optional[str] = Field("default", description="Certificate template type")


class CertificateResponse(BaseModel):
    """Response schema for certificate details."""

    id: uuid.UUID
    event_id: uuid.UUID
    student_id: uuid.UUID
    certificate_url: str
    issued_on: Optional[str]
    event: Optional[Dict[str, Any]]
    student: Optional[Dict[str, Any]]

    model_config = {"from_attributes": True}


class CertificateListResponse(BaseModel):
    """Response schema for paginated certificate list."""

    certificates: List[CertificateResponse]
    pagination: Dict[str, Any]

    model_config = {"from_attributes": True}


class DownloadCertificateRequest(BaseModel):
    """Request schema for downloading certificates."""

    # No additional fields needed, certificate ID is in URL
    pass


class BulkGenerateCertificatesRequest(BaseModel):
    """Request schema for bulk certificate generation."""

    event_id: uuid.UUID = Field(..., description="UUID of the event")
    generate_for_all_attendees: bool = Field(True, description="Generate for all attendees or specify student IDs")
    student_ids: Optional[List[uuid.UUID]] = Field(None, description="Specific student IDs (ignored if generate_for_all_attendees is True)")
    template_type: Optional[str] = Field("default", description="Certificate template type")


class CertificateGenerationResponse(BaseModel):
    """Response schema for certificate generation results."""

    success_count: int
    failed_count: int
    certificates: List[CertificateResponse]
    failed_generations: List[Dict[str, Any]]

    model_config = {"from_attributes": True}

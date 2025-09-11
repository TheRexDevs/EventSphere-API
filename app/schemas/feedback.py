"""
Pydantic schemas for Feedback management.

This module defines request and response schemas for feedback-related API operations
including submission, viewing, and management.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class SubmitFeedbackRequest(BaseModel):
    """Request schema for submitting feedback."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional written feedback")
    aspects: Optional[Dict[str, int]] = Field(None, description="Ratings for specific aspects (venue, coordination, etc.)")


class FeedbackResponse(BaseModel):
    """Response schema for feedback details."""

    id: uuid.UUID
    event_id: uuid.UUID
    student_id: uuid.UUID
    rating: int
    comment: Optional[str]
    aspects: Optional[Dict[str, int]]
    submitted_on: Optional[str]
    event: Optional[Dict[str, Any]]
    student: Optional[Dict[str, Any]]

    model_config = {"from_attributes": True}


class FeedbackListResponse(BaseModel):
    """Response schema for paginated feedback list."""

    feedback: List[FeedbackResponse]
    pagination: Dict[str, Any]
    summary: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class FeedbackStatsResponse(BaseModel):
    """Response schema for feedback statistics."""

    total_feedback: int
    average_rating: float
    rating_distribution: Dict[int, int]
    aspects_summary: Optional[Dict[str, Any]] = None
    recent_feedback: List[FeedbackResponse]

    model_config = {"from_attributes": True}


class UpdateFeedbackRequest(BaseModel):
    """Request schema for updating feedback."""

    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional written feedback")
    aspects: Optional[Dict[str, int]] = Field(None, description="Ratings for specific aspects")

    @field_validator('aspects')
    def validate_aspects(cls, v: Optional[Dict[str, int]]) -> Optional[Dict[str, int]]:
        """Validate aspect ratings are between 1-5."""
        if v is not None:
            for key, rating in v.items():
                if not (1 <= rating <= 5):
                    raise ValueError(f'Aspect rating for {key} must be between 1 and 5')
        return v

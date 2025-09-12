"""
Pydantic schemas for Event management.

This module defines request and response schemas for event-related API operations
including creation, updates, listing, and detailed responses.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class EventCategoryResponse(BaseModel):
    """Response schema for event category."""

    id: uuid.UUID
    name: str
    description: str

    model_config = {"from_attributes": True}


class EventOrganizerResponse(BaseModel):
    """Response schema for event organizer."""

    id: uuid.UUID
    username: str
    email: str
    full_name: Optional[str]

    model_config = {"from_attributes": True}


class CreateEventRequest(BaseModel):
    """Request schema for creating events."""

    title: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1)
    date: str = Field(..., description="ISO format date string (YYYY-MM-DD)")
    time: str = Field(..., description="ISO format time string (HH:MM:SS)")
    venue: str = Field(..., min_length=1, max_length=100)
    capacity: int = Field(0, ge=0, description="Maximum capacity (0 for unlimited)")
    max_participants: int = Field(0, ge=0, description="Maximum participants (0 for unlimited)")
    category_id: Optional[uuid.UUID] = None

    # Image fields
    featured_image_url: Optional[str] = Field(None, description="URL of the featured image")
    gallery_image_urls: List[str] = Field(default_factory=list, description="List of gallery image URLs")

    @field_validator('date')
    def validate_date(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v

    @field_validator('time')
    def validate_time(cls, v: str) -> str:
        """Validate time format."""
        try:
            datetime.strptime(v, '%H:%M:%S')
        except ValueError:
            raise ValueError('Invalid time format. Use HH:MM:SS')
        return v


class UpdateEventRequest(BaseModel):
    """Request schema for updating events."""

    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, min_length=1)
    date: Optional[str] = Field(None, description="ISO format date string (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="ISO format time string (HH:MM:SS)")
    venue: Optional[str] = Field(None, min_length=1, max_length=100)
    capacity: Optional[int] = Field(None, ge=0, description="Maximum capacity (0 for unlimited)")
    max_participants: Optional[int] = Field(None, ge=0, description="Maximum participants (0 for unlimited)")
    category_id: Optional[uuid.UUID] = None

    # Image fields
    featured_image_url: Optional[str] = Field(None, description="URL of the featured image")
    gallery_image_urls: Optional[List[str]] = Field(None, description="List of gallery image URLs")

    @field_validator('date')
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v

    @field_validator('time')
    def validate_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format."""
        if v is None:
            return v
        try:
            datetime.strptime(v, '%H:%M:%S')
        except ValueError:
            raise ValueError('Invalid time format. Use HH:MM:SS')
        return v


class EventImageResponse(BaseModel):
    """Response schema for event images."""

    id: uuid.UUID
    url: str
    thumbnail_url: Optional[str]
    filename: str
    width: Optional[int]
    height: Optional[int]

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    """Response schema for event details."""

    id: uuid.UUID
    title: str
    description: str
    date: Optional[str]
    time: Optional[str]
    venue: str
    capacity: int
    max_participants: int
    status: str
    organizer_id: Optional[uuid.UUID]
    organizer: Optional[EventOrganizerResponse]
    category_id: Optional[uuid.UUID]
    category: Optional[str]
    featured_image: Optional[EventImageResponse]
    gallery_images: List[EventImageResponse] = Field(default_factory=list)
    created_at: Optional[str]
    updated_at: Optional[str]

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Response schema for paginated event list."""

    events: List[EventResponse]
    pagination: Dict[str, Any]

    model_config = {"from_attributes": True}


class EventCategoriesResponse(BaseModel):
    """Response schema for event categories list."""

    categories: List[EventCategoryResponse]

    model_config = {"from_attributes": True}


class ApproveEventRequest(BaseModel):
    """Request schema for approving events (admin only)."""

    # No additional fields needed, approval is implicit
    pass


class PublishEventRequest(BaseModel):
    """Request schema for publishing events."""

    # No additional fields needed, publish status toggle
    pass

"""
Pydantic schemas for Registration management.

This module defines request and response schemas for registration-related API operations
including registration, cancellation, and listing.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class RegisterForEventRequest(BaseModel):
    """Request schema for registering for events."""

    # No additional fields needed, registration is based on event_id in URL
    pass


class CancelRegistrationRequest(BaseModel):
    """Request schema for canceling registration."""

    # No additional fields needed, cancellation is based on event_id in URL
    pass


class RegistrationStudentResponse(BaseModel):
    """Response schema for registration student info."""

    id: uuid.UUID
    username: str
    email: str
    full_name: Optional[str]

    model_config = {"from_attributes": True}


class RegistrationEventResponse(BaseModel):
    """Response schema for registration event info."""

    id: uuid.UUID
    title: str
    date: Optional[str]
    time: Optional[str]
    venue: str
    organizer: Optional[str]

    model_config = {"from_attributes": True}


class RegistrationResponse(BaseModel):
    """Response schema for registration details."""

    id: uuid.UUID
    event_id: uuid.UUID
    student_id: uuid.UUID
    registered_on: Optional[str]
    status: str
    event: Optional[RegistrationEventResponse]
    student: Optional[RegistrationStudentResponse]

    model_config = {"from_attributes": True}


class RegistrationListResponse(BaseModel):
    """Response schema for paginated registration list."""

    registrations: List[RegistrationResponse]
    pagination: Dict[str, Any]

    model_config = {"from_attributes": True}

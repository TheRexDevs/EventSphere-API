"""
Pydantic schemas for Attendance management.

This module defines request and response schemas for attendance-related API operations
including marking attendance and retrieving attendance reports.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class MarkAttendanceRequest(BaseModel):
    """Request schema for marking attendance."""

    event_id: uuid.UUID = Field(..., description="UUID of the event")
    student_id: uuid.UUID = Field(..., description="UUID of the student")


class AttendanceStudentResponse(BaseModel):
    """Response schema for attendance student info."""

    id: uuid.UUID
    username: str
    email: str
    full_name: Optional[str]

    model_config = {"from_attributes": True}


class AttendanceEventResponse(BaseModel):
    """Response schema for attendance event info."""

    id: uuid.UUID
    title: str
    date: Optional[str]
    venue: str

    model_config = {"from_attributes": True}


class AttendanceRecordResponse(BaseModel):
    """Response schema for individual attendance record."""

    id: uuid.UUID
    event_id: uuid.UUID
    student_id: uuid.UUID
    attended: bool
    marked_on: Optional[str]
    event: Optional[AttendanceEventResponse]
    student: Optional[AttendanceStudentResponse]

    model_config = {"from_attributes": True}


class AttendanceItemResponse(BaseModel):
    """Response schema for attendance list item."""

    registration_id: uuid.UUID
    student: AttendanceStudentResponse
    registered_on: Optional[str]
    attended: bool
    marked_on: Optional[str]

    model_config = {"from_attributes": True}


class EventAttendanceResponse(BaseModel):
    """Response schema for complete event attendance report."""

    event: Dict[str, Any]
    summary: Dict[str, Any]
    attendance: List[AttendanceItemResponse]

    model_config = {"from_attributes": True}

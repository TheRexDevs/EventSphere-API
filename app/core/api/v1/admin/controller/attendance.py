"""
Attendance Controller

Handles basic attendance marking and tracking for events.
Provides simple attendance management without QR codes for MVP.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional

from flask import request, g
from pydantic import ValidationError

from app.extensions import db
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils
from app.schemas.attendance import MarkAttendanceRequest


class AttendanceController:
    """Controller for attendance operations."""

    @staticmethod
    def mark_attendance():
        """Mark attendance for a participant (Admin/Organizer only)."""
        try:
            # Validate request data using Pydantic schema
            payload = MarkAttendanceRequest.model_validate(request.get_json())

            # Get current user (admin/organizer)
            current_user = g.user
            if not current_user:
                return error_response("Authentication required", 401)

            event_uuid = payload.event_id
            student_uuid = payload.student_id

            # Verify event exists and is approved
            event = Event.query.filter_by(
                id=event_uuid,
                status='approved'
            ).first()

            if not event:
                return error_response("Event not found or not approved", 404)

            # Check if user is organizer or admin
            if (event.organizer_id != current_user.id and
                current_user.role != 'admin'):
                return error_response("Insufficient permissions", 403)

            # Check if student is registered
            registration = Registration.query.filter_by(
                event_id=event_uuid,
                student_id=student_uuid,
                status='confirmed'
            ).first()

            if not registration:
                return error_response("Student is not registered for this event", 404)

            # Check if attendance already marked
            existing_attendance = Attendance.query.filter_by(
                event_id=event_uuid,
                student_id=student_uuid
            ).first()

            if existing_attendance:
                return error_response("Attendance already marked for this student", 409)

            # Create attendance record
            attendance = Attendance()
            attendance.event_id = event_uuid
            attendance.student_id = student_uuid
            attendance.attended = True

            db.session.add(attendance)
            db.session.commit()

            return success_response(
                "Attendance marked successfully",
                201,
                {"attendance": attendance.to_dict()}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {str(e)}", 400)
        except ValueError:
            return error_response("Invalid ID format", 400)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to mark attendance: {str(e)}", 500)

    @staticmethod
    def get_event_attendance(event_id: str):
        """Get attendance list for an event (Admin/Organizer only)."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Verify event exists
            event = Event.query.get(event_uuid)
            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            if (event.organizer_id != current_user.id and
                current_user.role != 'admin'):
                return error_response("Insufficient permissions", 403)

            # Get attendance records
            attendance_records = Attendance.query.filter_by(event_id=event_uuid).all()

            # Get registered students for comparison
            registrations = Registration.query.filter_by(
                event_id=event_uuid,
                status='confirmed'
            ).all()

            # Build attendance summary
            attendance_list = []
            attended_count = 0

            for reg in registrations:
                attendance_record = next(
                    (att for att in attendance_records if att.student_id == reg.student_id),
                    None
                )

                attendance_item = {
                    'registration_id': str(reg.id),
                    'student': {
                        'id': str(reg.student.id),
                        'username': reg.student.username,
                        'email': reg.student.email,
                        'full_name': reg.student.profile.full_name if reg.student.profile else None
                    },
                    'registered_on': reg.registered_on.isoformat() if reg.registered_on else None,
                    'attended': attendance_record.attended if attendance_record else False,
                    'marked_on': attendance_record.marked_on.isoformat() if attendance_record else None
                }

                attendance_list.append(attendance_item)
                if attendance_record and attendance_record.attended:
                    attended_count += 1

            return success_response(
                "Attendance list retrieved successfully",
                200,
                {
                    'event': {
                        'id': str(event.id),
                        'title': event.title,
                        'date': event.date.isoformat() if event.date else None
                    },
                    'summary': {
                        'total_registered': len(registrations),
                        'total_attended': attended_count,
                        'attendance_rate': round((attended_count / len(registrations)) * 100, 2) if registrations else 0
                    },
                    'attendance': attendance_list
                }
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            return error_response(f"Failed to retrieve attendance: {str(e)}", 500)

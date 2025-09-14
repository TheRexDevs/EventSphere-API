"""
Certificate Controller

Handles certificate generation, management, and distribution.
Integrates with attendance system to generate certificates for attendees.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import request, current_app

from app.extensions import db
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils
from app.utils.certificate_generator import certificate_generator
from app.schemas.certificate import GenerateCertificateRequest, BulkGenerateCertificatesRequest
from app.utils.helpers.user import get_current_user
from app.logging import log_error


class CertificateController:
    """Controller for certificate operations."""

    @staticmethod
    def generate_certificate():
        """Generate certificate for a participant (Admin/Organizer only)."""
        try:
            # Validate request data using Pydantic schema
            payload = GenerateCertificateRequest.model_validate(request.get_json())

            # Get current user (admin/organizer)
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Verify event exists and is approved
            event = Event.query.filter_by(
                id=payload.event_id,
                status='approved'
            ).first()

            if not event:
                return error_response("Event not found or not approved", 404)

            # Check permissions
            if (event.organizer_id != current_user.id):
                return error_response("Insufficient permissions", 403)

            certificates = []
            failed_generations = []

            for student_id in payload.student_ids:
                try:
                    # Check if student attended the event
                    attendance = Attendance.query.filter_by(
                        event_id=payload.event_id,
                        student_id=student_id,
                        attended=True
                    ).first()

                    if not attendance:
                        failed_generations.append({
                            'student_id': str(student_id),
                            'reason': 'Student did not attend the event'
                        })
                        continue

                    # Check if certificate already exists
                    existing_cert = Certificate.query.filter_by(
                        event_id=payload.event_id,
                        student_id=student_id
                    ).first()

                    if existing_cert:
                        failed_generations.append({
                            'student_id': str(student_id),
                            'reason': 'Certificate already exists'
                        })
                        continue

                    # Generate certificate URL (placeholder for now)
                    certificate_url = f"/certificates/{payload.event_id}/{student_id}.pdf"

                    # Create certificate record
                    certificate = Certificate()
                    certificate.event_id = payload.event_id
                    certificate.student_id = student_id
                    certificate.certificate_url = certificate_url
                    certificate.issued_on = DateTimeUtils.aware_utcnow()

                    db.session.add(certificate)
                    certificates.append(certificate)

                except Exception as e:
                    failed_generations.append({
                        'student_id': str(student_id),
                        'reason': str(e)
                    })

            db.session.commit()

            return success_response(
                "Certificates generated successfully",
                201,
                {
                    'success_count': len(certificates),
                    'failed_count': len(failed_generations),
                    'certificates': [cert.to_dict() for cert in certificates],
                    'failed_generations': failed_generations
                }
            )

        except Exception as e:
            db.session.rollback()
            log_error("Failed to generate certificates", e)
            return error_response(f"Failed to generate certificates: {str(e)}", 500)

    @staticmethod
    def get_event_certificates(event_id: str):
        """Get all certificates for an event (Admin/Organizer only)."""
        try:
            event_uuid = uuid.UUID(event_id)
            current_user = get_current_user()

            if not current_user:
                return error_response("Authentication required", 401)

            # Verify event exists
            event = Event.query.get(event_uuid)
            if not event:
                return error_response("Event not found", 404)

            # Check permissions
            if (event.organizer_id != current_user.id):
                return error_response("Insufficient permissions", 403)

            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))

            # Get certificates
            certificates_query = Certificate.query.filter_by(event_id=event_uuid)
            certificates = certificates_query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response(
                "Event certificates retrieved successfully",
                200,
                {
                    'event': {
                        'id': str(event.id),
                        'title': event.title,
                        'date': event.date.isoformat() if event.date else None
                    },
                    'certificates': [cert.to_dict() for cert in certificates.items],
                    'pagination': {
                        'page': certificates.page,
                        'per_page': certificates.per_page,
                        'total': certificates.total,
                        'pages': certificates.pages,
                        'has_next': certificates.has_next,
                        'has_prev': certificates.has_prev
                    }
                }
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            log_error("Failed to retrieve certificates", e)
            return error_response(f"Failed to retrieve certificates: {str(e)}", 500)

    @staticmethod
    def bulk_generate_certificates():
        """Generate certificates for all attendees of an event (Admin/Organizer only)."""
        try:
            # Validate request data using Pydantic schema
            payload = BulkGenerateCertificatesRequest.model_validate(request.get_json())

            # Get current user (admin/organizer)
            current_user = get_current_user()
            if not current_user:
                return error_response("Authentication required", 401)

            # Verify event exists and is approved
            event = Event.query.filter_by(
                id=payload.event_id,
                status='approved'
            ).first()

            if not event:
                return error_response("Event not found or not approved", 404)

            # Check permissions
            if (event.organizer_id != current_user.id):
                return error_response("Insufficient permissions", 403)

            # Determine which students to generate certificates for
            if payload.generate_for_all_attendees:
                # Get all attendees who don't have certificates yet
                attendees = db.session.query(Attendance.student_id).filter(
                    Attendance.event_id == payload.event_id,
                    Attendance.attended == True
                ).outerjoin(Certificate, (Certificate.event_id == payload.event_id) &
                           (Certificate.student_id == Attendance.student_id)).filter(
                    Certificate.id.is_(None)
                ).all()

                student_ids = [att.student_id for att in attendees]
            else:
                student_ids = payload.student_ids or []

            if not student_ids:
                return error_response("No eligible students found for certificate generation", 400)

            # Generate certificates
            certificates = []
            failed_generations = []

            for student_id in student_ids:
                try:
                    # Get registration for student data
                    registration = Registration.query.filter_by(
                        event_id=payload.event_id,
                        student_id=student_id,
                        status='confirmed'
                    ).first()

                    if not registration:
                        failed_generations.append({
                            'student_id': str(student_id),
                            'reason': 'Student not registered for this event'
                        })
                        continue

                    # Generate actual PDF certificate
                    certificate_id = uuid.uuid4()

                    # Get event and student data for PDF generation
                    event_data = {
                        'title': event.title,
                        'date': event.date.isoformat() if event.date else None,
                        'organizer': {
                            'username': event.organizer.username if event.organizer else 'Event Organizer'
                        }
                    }

                    student_data = {
                        'username': registration.student.username,
                        'full_name': registration.student.full_name if hasattr(registration.student, 'full_name') else registration.student.username
                    }

                    # Generate PDF
                    certificate_url = certificate_generator.generate_certificate(
                        certificate_id=certificate_id,
                        event_data=event_data,
                        student_data=student_data,
                        issued_date=DateTimeUtils.aware_utcnow()
                    )

                    # Create certificate record
                    certificate = Certificate()
                    certificate.id = certificate_id
                    certificate.event_id = payload.event_id
                    certificate.student_id = student_id
                    certificate.certificate_url = certificate_url
                    certificate.cloudinary_public_id = f"certificates/{registration.student.username}/certificate_{certificate_id}"
                    certificate.issued_on = DateTimeUtils.aware_utcnow()

                    db.session.add(certificate)
                    certificates.append(certificate)

                except Exception as e:
                    failed_generations.append({
                        'student_id': str(student_id),
                        'reason': str(e)
                    })

            db.session.commit()

            return success_response(
                "Bulk certificate generation completed",
                201,
                {
                    'success_count': len(certificates),
                    'failed_count': len(failed_generations),
                    'certificates': [cert.to_dict() for cert in certificates],
                    'failed_generations': failed_generations
                }
            )

        except Exception as e:
            db.session.rollback()
            log_error("Failed to generate certificates", e)
            return error_response(f"Failed to generate certificates: {str(e)}", 500)

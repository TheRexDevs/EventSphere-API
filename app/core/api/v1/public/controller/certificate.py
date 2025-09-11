"""
Public Certificate Controller

Handles certificate download and viewing for authenticated participants.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional

from flask import request, g, send_file, current_app
import io
from pathlib import Path

from app.extensions import db
from app.models.certificate import Certificate
from app.utils.helpers.http_response import success_response, error_response
from app.utils.certificate_generator import certificate_generator


class PublicCertificateController:
    """Controller for public certificate operations."""

    @staticmethod
    def download_certificate(certificate_id: str):
        """Download a certificate PDF file (Participant only)."""
        try:
            cert_uuid = uuid.UUID(certificate_id)
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Find certificate
            certificate = Certificate.query.filter_by(
                id=cert_uuid,
                student_id=current_user.id
            ).first()

            if not certificate:
                return error_response("Certificate not found or access denied", 404)

            # Check if it's a Cloudinary URL
            if certificate.certificate_url.startswith('http'):
                # Redirect to Cloudinary URL
                from flask import redirect
                return redirect(certificate.certificate_url)
            else:
                # Local file - get the actual file path
                cert_file_path = certificate_generator.get_certificate_path(cert_uuid)

                if not cert_file_path or not cert_file_path.exists():
                    return error_response("Certificate file not found on server", 404)

                # Return the PDF file for download
                return send_file(
                    cert_file_path,
                    as_attachment=True,
                    download_name=f"certificate_{cert_uuid}.pdf",
                    mimetype='application/pdf'
                )

        except ValueError:
            return error_response("Invalid certificate ID format", 400)
        except Exception as e:
            return error_response(f"Failed to download certificate: {str(e)}", 500)

    @staticmethod
    def get_user_certificates():
        """Get current user's certificates (Participant only)."""
        try:
            current_user = g.user

            if not current_user:
                return error_response("Authentication required", 401)

            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))

            # Get certificates
            certificates = Certificate.query.filter_by(
                student_id=current_user.id
            ).order_by(Certificate.issued_on.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(
                "User certificates retrieved successfully",
                200,
                {
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

        except Exception as e:
            return error_response(f"Failed to retrieve certificates: {str(e)}", 500)

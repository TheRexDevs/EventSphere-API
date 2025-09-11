"""
Certificate PDF Generator Package

Generates professional certificate PDFs for event participants using ReportLab.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, gold, navy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from flask import current_app
from app.utils.media_service.uploaders import CloudinaryUploader


class CertificateGenerator:
    """Generates professional certificate PDFs."""

    def __init__(self):
        self.certificates_dir = self._ensure_certificates_directory()
        self._fallback_used = False

    def _ensure_certificates_directory(self) -> Path:
        """Ensure certificates directory exists."""
        try:
            cert_dir = Path(current_app.root_path) / "static" / "certificates"
            self._fallback_used = False
        except RuntimeError:
            # No application context, use current working directory as fallback
            cert_dir = Path.cwd() / "static" / "certificates"
            self._fallback_used = True

        cert_dir.mkdir(parents=True, exist_ok=True)
        return cert_dir

    def refresh_certificates_directory(self):
        """Refresh certificates directory to use proper app path when context becomes available."""
        if self._fallback_used:
            try:
                new_cert_dir = Path(current_app.root_path) / "static" / "certificates"
                new_cert_dir.mkdir(parents=True, exist_ok=True)
                self.certificates_dir = new_cert_dir
                self._fallback_used = False
            except RuntimeError:
                # Still no app context, keep current directory
                pass

    def generate_certificate(
        self,
        certificate_id: uuid.UUID,
        event_data: Dict[str, Any],
        student_data: Dict[str, Any],
        issued_date: datetime
    ) -> str:
        """
        Generate a certificate PDF.

        Args:
            certificate_id: Unique certificate identifier
            event_data: Event information (title, date, organizer)
            student_data: Student information (name, enrollment)
            issued_date: Date certificate was issued

        Returns:
            str: Cloudinary URL to generated PDF file
        """
        # Create filename
        filename = f"certificate_{certificate_id}.pdf"
        filepath = self.certificates_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=landscape(letter),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = ParagraphStyle(
            'CertificateTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=navy,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'CertificateSubtitle',
            parent=styles['Heading2'],
            fontSize=24,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )

        name_style = ParagraphStyle(
            'ParticipantName',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=gold,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica'
        )

        # Build content
        content = []

        # Title
        content.append(Paragraph("CERTIFICATE OF PARTICIPATION", title_style))
        content.append(Spacer(1, 20))

        # Subtitle
        content.append(Paragraph("This is to certify that", subtitle_style))
        content.append(Spacer(1, 15))

        # Participant Name
        participant_name = student_data.get('full_name', student_data.get('username', 'Participant'))
        content.append(Paragraph(participant_name, name_style))
        content.append(Spacer(1, 10))

        # Participation text
        content.append(Paragraph("has successfully participated in", body_style))
        content.append(Spacer(1, 5))

        # Event title
        event_title = event_data.get('title', 'Event')
        content.append(Paragraph(f"<b>{event_title}</b>", body_style))
        content.append(Spacer(1, 10))

        # Event details
        event_date = event_data.get('date', '')
        if event_date:
            if isinstance(event_date, str):
                event_date = datetime.fromisoformat(event_date).strftime('%B %d, %Y')
            content.append(Paragraph(f"held on {event_date}", body_style))

        # Organizer
        organizer_name = event_data.get('organizer', {}).get('username', 'Event Organizer')
        content.append(Spacer(1, 15))
        content.append(Paragraph(f"Organized by: {organizer_name}", body_style))

        # Issued date
        issued_str = issued_date.strftime('%B %d, %Y')
        content.append(Spacer(1, 20))
        content.append(Paragraph(f"Issued on: {issued_str}", body_style))

        # Certificate ID
        content.append(Spacer(1, 15))
        content.append(Paragraph(f"Certificate ID: {certificate_id}", ParagraphStyle(
            'CertificateID',
            parent=styles['Normal'],
            fontSize=10,
            textColor=Color(0.5, 0.5, 0.5),
            alignment=TA_LEFT
        )))

        # Build the PDF
        doc.build(content)

        # Upload generated PDF to Cloudinary (organized by username)
        username = student_data.get('username', 'unknown')
        folder = f"certificates/{username}"
        public_id = f"certificate_{certificate_id}"

        # Open the file and upload as raw resource (pdf)
        try:
            with open(filepath, 'rb') as fh:
                file_bytes = fh.read()
                result = CloudinaryUploader.upload_to_cloudinary(
                    file=file_bytes,
                    public_id=public_id,
                    folder=folder,
                    resource_type='raw',
                    optimization=False
                )

            # Remove local file after successful upload
            try:
                filepath.unlink()
            except Exception:
                pass

            # Return secure URL if available, otherwise return cloudinary url
            return result.get('secure_url') or result.get('url') or ''
        except Exception:
            # If upload fails, fallback to local path
            return f"/static/certificates/{filename}"

    def get_certificate_path(self, certificate_id: uuid.UUID) -> Optional[Path]:
        """Get the file path for a certificate."""
        filename = f"certificate_{certificate_id}.pdf"
        filepath = self.certificates_dir / filename

        if filepath.exists():
            return filepath
        return None

    def delete_certificate(self, certificate_id: uuid.UUID) -> bool:
        """Delete a certificate file."""
        filepath = self.certificates_dir / f"certificate_{certificate_id}.pdf"
        try:
            if filepath.exists():
                filepath.unlink()
                return True
        except Exception:
            pass
        return False

    def delete_certificate_from_cloudinary(self, public_id: str) -> bool:
        """Delete a certificate from Cloudinary."""
        return CloudinaryUploader.delete_from_cloudinary(public_id)


# Lazy-loaded global instance
_certificate_generator = None

def get_certificate_generator() -> CertificateGenerator:
    """Get the global certificate generator instance."""
    global _certificate_generator
    if _certificate_generator is None:
        _certificate_generator = CertificateGenerator()
    else:
        # Refresh directory in case app context is now available
        _certificate_generator.refresh_certificates_directory()
    return _certificate_generator

# For backward compatibility, provide a property-like access
class _CertificateGeneratorProxy:
    """Proxy to lazily create certificate generator."""

    def __getattr__(self, name):
        return getattr(get_certificate_generator(), name)

# Global proxy instance
certificate_generator = _CertificateGeneratorProxy()

# Export the main class and instance for easy importing
__all__ = ['CertificateGenerator', 'certificate_generator', 'get_certificate_generator']

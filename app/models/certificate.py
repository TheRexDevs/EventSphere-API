"""
Certificate model

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped as M, relationship

from app.extensions import db
from app.utils.date_time import DateTimeUtils

# Forward declarations for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import AppUser
    from .event import Event


class Certificate(db.Model):
    __tablename__ = "certificate"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey('event.id'), nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_user.id'), nullable=False)
    certificate_url = db.Column(db.String(255), nullable=False)
    cloudinary_public_id = db.Column(db.String(255), nullable=True, index=True)
    issued_on = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    
    event = db.relationship('Event', backref=db.backref('certificates', lazy='dynamic'))
    student = db.relationship('AppUser', backref=db.backref('certificates', lazy='dynamic'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert certificate instance to dictionary representation."""
        return {
            'id': str(self.id),
            'event_id': str(self.event_id),
            'student_id': str(self.student_id),
            'certificate_url': self.certificate_url,
            'cloudinary_public_id': self.cloudinary_public_id,
            'issued_on': self.issued_on.isoformat() if self.issued_on else None,
            'event': {
                'id': str(self.event.id),
                'title': self.event.title,
                'date': self.event.date.isoformat() if self.event.date else None,
                'venue': self.event.venue
            } if self.event else None,
            'student': {
                'id': str(self.student.id),
                'username': self.student.username,
                'email': self.student.email,
                'full_name': self.student.full_name if hasattr(self.student, 'full_name') else None
            } if self.student else None,
        }

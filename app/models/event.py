"""
Event model

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
    from .media import Media



class Event(db.Model):
    __tablename__ = "event"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending, approved, cancelled
    max_participants = db.Column(db.Integer, default=0)
    organizer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_user.id'))
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('event_category.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)
    
    organizer = db.relationship('AppUser', backref=db.backref('organized_events', lazy='dynamic'))
    media = db.relationship('Media', back_populates='event', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Media.event_id')
    category = relationship("EventCategory", back_populates="events")

    # Image fields for featured image and gallery
    featured_image_id = db.Column(UUID(as_uuid=True), db.ForeignKey('media.id'), nullable=True)
    featured_image = db.relationship('Media', foreign_keys=[featured_image_id], lazy='joined')

    @property
    def safe_media_list(self) -> List["Media"]:
        """Safely get media list, handling lazy loading."""
        try:
            if hasattr(self, 'media') and self.media is not None:
                if hasattr(self.media, 'all'):
                    # For dynamic relationships
                    return self.media.all()  # type: ignore
                else:
                    # For already loaded collections or other iterables
                    result = []
                    media_collection = self.media  # type: ignore
                    for item in media_collection:  # type: ignore
                        result.append(item)
                    return result
        except (AttributeError, TypeError):
            pass
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert event instance to dictionary representation."""
        # Get featured image
        featured_image = None
        if hasattr(self, 'featured_image') and self.featured_image:
            featured_image = {
                'id': str(self.featured_image.id),
                'url': self.featured_image.file_url,
                'thumbnail_url': self.featured_image.thumbnail_url,
                'filename': self.featured_image.filename,
                'width': self.featured_image.width,
                'height': self.featured_image.height,
            }

        # Get gallery images (all media except featured)
        gallery_images = []
        for media in self.safe_media_list:
            if hasattr(media, 'is_featured') and not media.is_featured:  # Exclude featured image from gallery
                gallery_images.append({
                    'id': str(media.id),
                    'url': media.file_url,
                    'thumbnail_url': media.thumbnail_url,
                    'filename': media.filename,
                    'width': media.width,
                    'height': media.height,
                    'file_type': media.file_type,
                    'created_at': media.created_at.isoformat() if media.created_at else None,
                })

        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'venue': self.venue,
            'capacity': self.capacity,
            'max_participants': self.max_participants,
            'status': self.status,
            'organizer_id': str(self.organizer_id) if self.organizer_id else None,
            'organizer': {
                'id': str(self.organizer.id),
                'username': self.organizer.username,
                'email': self.organizer.email,
                'full_name': self.organizer.profile.full_name if self.organizer.profile else None
            } if self.organizer else None,
            'category_id': str(self.category_id) if self.category_id else None,
            'category': self.category.name if self.category else None,
            'featured_image': featured_image,
            'gallery_images': gallery_images,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class EventCategory(db.Model):
    __tablename__ = "event_category"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    events = relationship("Event", back_populates="category")


class EventShareLog(db.Model):
    __tablename__ = "event_share_log"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_user.id'), nullable=False)
    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey('event.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False) # Facebook, WhatsApp, etc.
    share_timestamp = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    share_message = db.Column(db.Text)
    
    event = db.relationship('Event', backref=db.backref('share_logs', lazy='dynamic'))
    student = db.relationship('AppUser', backref=db.backref('share_logs', lazy='dynamic'))




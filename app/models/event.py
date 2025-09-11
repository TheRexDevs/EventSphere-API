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
    
    organizer = db.relationship('AppUser', backref=db.backref('organized_events', lazy='dynamic'))
    media = db.relationship('Media', back_populates='event', lazy='dynamic', cascade='all, delete-orphan')


class EventCategory(db.Model):
    __tablename__ = "event_category"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    events = relationship("Event", backref="category_ref")


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




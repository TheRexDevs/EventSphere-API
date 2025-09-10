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



class Event(db.Model):
    __tablename__ = "event"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=0)
    organizer_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('event_category.id'), nullable=True)
    
    media = db.relationship('Media', back_populates='event', lazy='dynamic', cascade='all, delete-orphan')


class EventCategory(db.Model):
    __tablename__ = "event_category"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    events = relationship("Event", backref="category_ref")
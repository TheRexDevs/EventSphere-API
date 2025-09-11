"""
This package contains the database models for the Flask application.

Each model corresponds to a table in the database.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
Package: EventSphere
"""
from flask import Flask
from sqlalchemy.orm import aliased

from .user import AppUser, Profile, Address, TempUser
from .role import Role, UserRole
from .event import Event, EventCategory, EventShareLog
from .registration import Registration
from .attendance import Attendance
from .feedback import Feedback
from .certificate import Certificate
from .waitlist import Waitlist
from .calendar_sync import CalendarSync
from .media import Media

from .wallet import Wallet
from .payment import Payment, Transaction
from .subscription import Subscription, SubscriptionPlan

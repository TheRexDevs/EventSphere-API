"""
This package contains the database models for the Flask application.

It includes models for User, Product, Category, Role, etc. Each model corresponds to a table in the database.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: EventSphere
"""
from flask import Flask
from sqlalchemy.orm import aliased

from .media import Media
from .user import AppUser, Profile, Address, TempUser
from .role import Role, UserRole
from .wallet import Wallet
from .event import Event

from .payment import Payment, Transaction
from .subscription import Subscription, SubscriptionPlan

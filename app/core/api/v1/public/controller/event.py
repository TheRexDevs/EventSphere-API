"""
Public Event Controller

Handles public event browsing and basic event information access
for all users (authenticated and non-authenticated).

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional

from flask import request
from sqlalchemy import or_

from app.extensions import db
from app.models.event import Event
from app.utils.helpers.http_response import success_response, error_response


class PublicEventController:
    """Controller for public event operations."""

    @staticmethod
    def get_events():
        """Get public events (approved only) with basic filtering."""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            search = request.args.get('search')
            category = request.args.get('category')
            venue = request.args.get('venue')

            # Build query - only approved events
            query = Event.query.filter_by(status='approved')

            if search:
                query = query.filter(
                    or_(
                        Event.title.ilike(f'%{search}%'),
                        Event.description.ilike(f'%{search}%'),
                        Event.venue.ilike(f'%{search}%')
                    )
                )

            if category:
                query = query.filter(Event.category.has(name=category))

            if venue:
                query = query.filter(Event.venue.ilike(f'%{venue}%'))

            # Paginate
            events = query.order_by(Event.date.asc(), Event.time.asc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(
                "Events retrieved successfully",
                200,
                {
                    'events': [event.to_dict() for event in events.items],
                    'pagination': {
                        'page': events.page,
                        'per_page': events.per_page,
                        'total': events.total,
                        'pages': events.pages,
                        'has_next': events.has_next,
                        'has_prev': events.has_prev
                    }
                }
            )

        except Exception as e:
            return error_response(f"Failed to retrieve events: {str(e)}", 500)

    @staticmethod
    def get_event(event_id: str):
        """Get a specific public event by ID."""
        try:
            event_uuid = uuid.UUID(event_id)
            event = Event.query.filter_by(
                id=event_uuid,
                status='approved'
            ).first()

            if not event:
                return error_response("Event not found", 404)

            return success_response(
                "Event retrieved successfully",
                200,
                {"event": event.to_dict()}
            )

        except ValueError:
            return error_response("Invalid event ID format", 400)
        except Exception as e:
            return error_response(f"Failed to retrieve event: {str(e)}", 500)

    @staticmethod
    def get_event_categories():
        """Get all available event categories."""
        try:
            from app.models.event import EventCategory
            categories: List[EventCategory] = EventCategory.query.all()

            return success_response(
                "Categories retrieved successfully",
                200,
                {
                    'categories': [
                        {
                            'id': str(cat.id),
                            'name': cat.name,
                            'description': cat.description
                        } for cat in categories
                    ]
                }
            )

        except Exception as e:
            return error_response(f"Failed to retrieve categories: {str(e)}", 500)

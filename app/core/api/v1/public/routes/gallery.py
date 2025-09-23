"""
Events Gallery routes for the public API.

This module defines all gallery-related endpoints including listing,
and stats

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import MediaController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, SecurityScheme, QueryParameter
from app.schemas.common import ApiResponse

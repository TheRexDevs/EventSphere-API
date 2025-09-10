"""System endpoints for Admin API v1."""

from __future__ import annotations

from typing import Dict, Any

from app.utils.helpers.http_response import success_response
from ..controller import get_admin_root, get_admin_health


def register_routes(bp):
    @bp.get("/")
    def admin_index():
        """Return a minimal response for the admin v1 API root."""
        data: Dict[str, Any] = get_admin_root()
        return success_response("ok", 200, data)


    @bp.get("/health")
    def admin_health():
        """Health endpoint for the admin v1 API."""
        data: Dict[str, Any] = get_admin_health()
        return success_response("ok", 200, data)
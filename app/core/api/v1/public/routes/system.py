"""System endpoints for Public API v1."""

from __future__ import annotations

from ..controller import SystemController


def register_routes(bp):
    @bp.get("/")
    def public_index():
        """Return a minimal response for the public v1 API root."""
        return SystemController.get_public_root()


    @bp.get("/health")
    def public_health():
        """Health endpoint for the public v1 API."""
        return SystemController.get_public_health()



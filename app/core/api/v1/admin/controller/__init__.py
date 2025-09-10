"""Controllers for Admin API v1."""

from __future__ import annotations

from typing import Dict, Any


def get_admin_root() -> Dict[str, Any]:
    """Return metadata for the admin v1 API root."""
    return {
        "service": "admin",
        "version": "v1",
    }


def get_admin_health() -> Dict[str, Any]:
    """Return health data for the admin v1 API."""
    return {"healthy": True}


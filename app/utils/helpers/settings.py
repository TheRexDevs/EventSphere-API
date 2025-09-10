"""
Settings helper shims.

This module centralizes access to platform settings that would typically be
stored in a database or environment variables. For now, it provides minimal
helpers used by payments. Later, these can be wired to real persistence.
"""

from __future__ import annotations

from typing import Any, Optional
from flask import current_app


def get_general_setting(key: str, default: Any | None = None) -> Any:
    """Fetch a general platform setting, falling back to app config or default."""
    return current_app.config.get(key, default)


def get_active_payment_gateway() -> Optional[dict]:
    """
    Return the active payment gateway configuration.

    Expected structure:
    {
        "provider": "flutterwave" | "paystack" | "bitpay",
        "credentials": {
            "api_key": "...",
            "secret_key": "...",
            "public_key": "...",
            "test_mode": "true" | "false",
            "test_api_key": "...",
            "test_secret_key": "...",
            "test_public_key": "..."
        }
    }
    """
    return current_app.config.get("PAYMENT_GATEWAY")


def get_platform_url() -> str:
    """Return the platform base URL used for redirects in payment flows."""
    return current_app.config.get("APP_DOMAIN_NAME", "http://localhost:3000")


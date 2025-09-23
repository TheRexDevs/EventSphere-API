"""Password reset token management using application cache.

Stores password reset tokens securely with expiration and rate limiting.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import timedelta as _timedelta
import hashlib
import json
import uuid
from typing import Optional

from app.extensions import app_cache


@dataclass
class PasswordResetToken:
    """Ephemeral record for a password reset request."""

    user_id: str  # UUID string of the user
    email: str
    token_hash: str  # Hashed version of the actual JWT token
    attempts: int = 0

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(data: str) -> "PasswordResetToken":
        obj = json.loads(data)
        return PasswordResetToken(**obj)


def _key(token_hash: str) -> str:
    return f"password_reset:{token_hash}"


def _rate_limit_key(email: str) -> str:
    return f"password_reset_rate_limit:{email}"


def generate_reset_token() -> str:
    """Generate a JWT-compatible token string."""
    return uuid.uuid4().hex + uuid.uuid4().hex  # 64 character token


def hash_token(token: str) -> str:
    """Hash a reset token for secure storage."""
    h = hashlib.sha256()
    h.update(token.encode("utf-8"))
    return h.hexdigest()


def store_password_reset_token(token_hash: str, reset_data: PasswordResetToken, ttl_minutes: int = 30) -> None:
    """Store a password reset token with TTL."""
    app_cache.set(_key(token_hash), reset_data.to_json(), timeout=int(_timedelta(minutes=ttl_minutes).total_seconds()))


def get_password_reset_token(token_hash: str) -> Optional[PasswordResetToken]:
    """Fetch a password reset token, or None if expired/missing."""
    raw = app_cache.get(_key(token_hash))
    if not raw:
        return None
    try:
        return PasswordResetToken.from_json(raw)  # type: ignore[arg-type]
    except Exception:
        return None


def delete_password_reset_token(token_hash: str) -> None:
    """Delete a password reset token."""
    app_cache.delete(_key(token_hash))


def increment_token_attempts(token_hash: str) -> int:
    """Increment validation attempts counter and persist; returns the new attempts value."""
    rec = get_password_reset_token(token_hash)
    if rec is None:
        return 0
    rec.attempts += 1
    # Preserve existing TTL by not specifying new TTL
    store_password_reset_token(token_hash, rec)
    return rec.attempts


def check_rate_limit(email: str, max_attempts: int = 3, window_minutes: int = 15) -> tuple[bool, int]:
    """Check if email is rate limited for password reset requests.

    Returns (is_limited, remaining_attempts).
    """
    key = _rate_limit_key(email)
    attempts = app_cache.get(key) or 0

    if attempts >= max_attempts:
        return True, 0

    return False, max_attempts - attempts


def increment_rate_limit(email: str, window_minutes: int = 15) -> int:
    """Increment rate limit counter for email and return new count."""
    key = _rate_limit_key(email)
    attempts = app_cache.get(key) or 0
    attempts += 1

    # Set/update TTL on each increment
    app_cache.set(key, attempts, timeout=int(_timedelta(minutes=window_minutes).total_seconds()))

    return attempts


def reset_rate_limit(email: str) -> None:
    """Reset rate limit counter for email."""
    key = _rate_limit_key(email)
    app_cache.delete(key)

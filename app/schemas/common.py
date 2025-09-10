"""Common Pydantic schemas used in API responses."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel
from typing_extensions import Literal


class ApiResponse(BaseModel):
    """Canonical API response envelope."""

    status: Literal['success', 'failed']
    status_code: int
    message: str
    data: Any | None = None



"""Pydantic schemas for auth endpoints."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    firstname: str = Field(min_length=1)
    lastname: str | None = None
    username: str | None = None
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    """Schema for user login."""

    email_username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class VerifyEmailRequest(BaseModel):
    """Schema for email verification."""

    reg_id: str = Field(min_length=8)
    code: str = Field(min_length=4, max_length=8)


class ResendCodeRequest(BaseModel):
    """Schema for resending verification code."""

    reg_id: str = Field(min_length=8)


class ValidateTokenRequest(BaseModel):
    """Schema for token validation."""

    token: str = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh."""

    token: str = Field(min_length=1)


class CheckEmailRequest(BaseModel):
    """Schema for email availability check."""

    email: EmailStr


class CheckUsernameRequest(BaseModel):
    """Schema for username availability check."""

    username: str = Field(min_length=1)


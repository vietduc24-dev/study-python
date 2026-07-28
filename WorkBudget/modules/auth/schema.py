"""Auth request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    default_currency: str = Field(default="VND", min_length=3, max_length=3)
    timezone: str = Field(default="Asia/Tokyo", min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize and lightly validate email."""
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Invalid email")
        return normalized

    @field_validator("default_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        """Normalize ISO-like currency code."""
        return value.strip().upper()


class RegisterResponse(BaseModel):
    """Response after creating a pending registration."""

    user_id: UUID
    registration_id: UUID
    status: str
    verification_token: str
    expires_at: datetime


class VerifyRegistrationRequest(BaseModel):
    """Request body for verifying a pending registration."""

    email: str = Field(min_length=3, max_length=320)
    verification_token: str = Field(min_length=16)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email."""
        return value.strip().lower()


class VerifyRegistrationResponse(BaseModel):
    """Response after verifying registration."""

    user_id: UUID
    status: str
    email_verified_at: datetime


class LoginRequest(BaseModel):
    """Request body for login."""

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email."""
        return value.strip().lower()


class TokenResponse(BaseModel):
    """Access and refresh token response."""

    token_type: str = "bearer"
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class RefreshTokenRequest(BaseModel):
    """Request body for refreshing tokens."""

    refresh_token: str = Field(min_length=16)


class LogoutRequest(BaseModel):
    """Request body for logout."""

    refresh_token: str = Field(min_length=16)


class LogoutResponse(BaseModel):
    """Logout response."""

    revoked: bool


class CurrentUserResponse(BaseModel):
    """Current authenticated user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    default_currency: str
    timezone: str
    email_verified_at: datetime | None

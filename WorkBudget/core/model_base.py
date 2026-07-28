"""Shared SQLAlchemy model primitives."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid6 import uuid7


def new_uuid_v7() -> UUID:
    """Generate a time-ordered UUIDv7 value in the application layer."""
    return uuid7()


class TimestampMixin:
    """Common timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class SoftDeleteMixin:
    """Soft-delete marker for user-facing records."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

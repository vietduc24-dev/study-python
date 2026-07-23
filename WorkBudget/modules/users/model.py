"""Users persistence models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import SoftDeleteMixin, TimestampMixin, new_uuid_v7


class User(TimestampMixin, SoftDeleteMixin, Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text)
    default_currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

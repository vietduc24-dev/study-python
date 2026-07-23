"""Auth persistence models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import TimestampMixin, new_uuid_v7


class LoginSession(TimestampMixin, Base):
    """Login session storing token hashes and lifecycle metadata."""

    __tablename__ = "login_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(Text)
    access_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    refresh_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("uq_login_sessions_access_token_hash", "access_token_hash", unique=True),
        Index(
            "uq_login_sessions_refresh_token_hash",
            "refresh_token_hash",
            unique=True,
        ),
        Index(
            "ix_login_sessions_user_active",
            "user_id",
            "refresh_expires_at",
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )


class UserRegistration(TimestampMixin, Base):
    """Pending or completed user registration flow."""

    __tablename__ = "user_registrations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    email: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    verification_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "uq_user_registrations_email_pending",
            "email",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
        Index(
            "uq_user_registrations_verification_token_hash",
            "verification_token_hash",
            unique=True,
        ),
        Index(
            "ix_user_registrations_status_expires",
            "status",
            "expires_at",
        ),
    )

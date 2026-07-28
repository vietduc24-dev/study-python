"""Workspace persistence models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import SoftDeleteMixin, TimestampMixin, new_uuid_v7


class Group(TimestampMixin, SoftDeleteMixin, Base):
    """Shared workspace/group."""

    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    default_currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)


class GroupMember(TimestampMixin, Base):
    """Membership between a user and a group."""

    __tablename__ = "group_members"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("uq_group_members_group_user", "group_id", "user_id", unique=True),
        Index("ix_group_members_user_id", "user_id"),
    )

"""Notifications persistence models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import TimestampMixin, new_uuid_v7


class Reminder(TimestampMixin, Base):
    """Reminder for one user and exactly one target item."""

    __tablename__ = "reminders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    personal_task_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("personal_tasks.id")
    )
    group_task_id: Mapped[UUID | None] = mapped_column(ForeignKey("group_tasks.id"))
    schedule_id: Mapped[UUID | None] = mapped_column(ForeignKey("group_schedules.id"))
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(personal_task_id, group_task_id, schedule_id) = 1",
            name="reminder_has_exactly_one_target",
        ),
        Index(
            "ix_reminders_user_pending_remind_at",
            "user_id",
            "remind_at",
            postgresql_where=text("status = 'pending'"),
        ),
    )

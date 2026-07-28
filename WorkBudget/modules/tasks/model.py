"""Tasks persistence models."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import SoftDeleteMixin, TimestampMixin, new_uuid_v7


class PersonalTask(TimestampMixin, SoftDeleteMixin, Base):
    """Task owned by one user."""

    __tablename__ = "personal_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_personal_tasks_user_status_due", "user_id", "status", "due_date"),
    )


class GroupSchedule(TimestampMixin, SoftDeleteMixin, Base):
    """Schedule item owned by a group."""

    __tablename__ = "group_schedules"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    repeat_rule: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("ix_group_schedules_group_start", "group_id", "start_time"),
    )


class ScheduleAssignee(TimestampMixin, Base):
    """Assigned user for a group schedule."""

    __tablename__ = "schedule_assignees"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    schedule_id: Mapped[UUID] = mapped_column(
        ForeignKey("group_schedules.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index(
            "uq_schedule_assignees_schedule_user",
            "schedule_id",
            "user_id",
            unique=True,
        ),
        Index("ix_schedule_assignees_user_id", "user_id"),
    )


class GroupTask(TimestampMixin, SoftDeleteMixin, Base):
    """Task owned by a group."""

    __tablename__ = "group_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_group_tasks_group_status_due", "group_id", "status", "due_date"),
    )


class TaskAssignee(TimestampMixin, Base):
    """Assigned user for a group task."""

    __tablename__ = "task_assignees"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("group_tasks.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("uq_task_assignees_task_user", "task_id", "user_id", unique=True),
        Index("ix_task_assignees_user_id", "user_id"),
    )

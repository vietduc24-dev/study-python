"""SQLAlchemy models used by Alembic migrations and repositories."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import CHAR
from uuid6 import uuid7

from WorkBudget.core.database import Base


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


class User(TimestampMixin, SoftDeleteMixin, Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    default_currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


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
        Index("uq_login_sessions_refresh_token_hash", "refresh_token_hash", unique=True),
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
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
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


class Category(TimestampMixin, SoftDeleteMixin, Base):
    """Personal or group expense category."""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[UUID | None] = mapped_column(ForeignKey("groups.id"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND group_id IS NULL) OR "
            "(user_id IS NULL AND group_id IS NOT NULL)",
            name="category_has_exactly_one_owner",
        ),
        Index(
            "uq_categories_user_name_active",
            "user_id",
            "name",
            unique=True,
            postgresql_where=text("group_id IS NULL AND deleted_at IS NULL"),
        ),
        Index(
            "uq_categories_group_name_active",
            "group_id",
            "name",
            unique=True,
            postgresql_where=text("user_id IS NULL AND deleted_at IS NULL"),
        ),
    )


class Expense(TimestampMixin, SoftDeleteMixin, Base):
    """Personal expense."""

    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="expense_amount_positive"),
        Index("ix_expenses_user_date", "user_id", expense_date.desc()),
        Index("ix_expenses_category_id", "category_id"),
    )


class PersonalBudget(TimestampMixin, SoftDeleteMixin, Base):
    """Personal budget for a category and period."""

    __tablename__ = "personal_budgets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    limit_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    period: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "limit_amount_minor > 0", name="personal_budget_limit_positive"
        ),
        Index(
            "ix_personal_budgets_user_period_dates",
            "user_id",
            "period",
            "start_date",
            "end_date",
        ),
    )


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
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
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


class SharedExpense(TimestampMixin, SoftDeleteMixin, Base):
    """Expense tracked inside a group."""

    __tablename__ = "shared_expenses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    paid_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="shared_expense_amount_positive"),
        Index("ix_shared_expenses_group_date", "group_id", expense_date.desc()),
        Index("ix_shared_expenses_paid_by_user_id", "paid_by_user_id"),
    )


class Reminder(TimestampMixin, Base):
    """Reminder for one user and exactly one target item."""

    __tablename__ = "reminders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    personal_task_id: Mapped[UUID | None] = mapped_column(ForeignKey("personal_tasks.id"))
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

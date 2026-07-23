"""Finance persistence models."""

from datetime import date
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import SoftDeleteMixin, TimestampMixin, new_uuid_v7


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


class SharedExpense(TimestampMixin, SoftDeleteMixin, Base):
    """Expense tracked inside a group."""

    __tablename__ = "shared_expenses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid_v7)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    paid_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="shared_expense_amount_positive"),
        Index("ix_shared_expenses_group_date", "group_id", expense_date.desc()),
        Index("ix_shared_expenses_paid_by_user_id", "paid_by_user_id"),
    )

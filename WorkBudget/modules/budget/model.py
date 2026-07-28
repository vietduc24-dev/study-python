"""Budget persistence models."""

from datetime import date
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR

from WorkBudget.core.database import Base
from WorkBudget.core.model_base import SoftDeleteMixin, TimestampMixin, new_uuid_v7


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

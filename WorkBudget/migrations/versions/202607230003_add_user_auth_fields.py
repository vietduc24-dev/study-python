"""Add user auth fields.

Revision ID: 202607230003
Revises: 202607230002
Create Date: 2026-07-23 00:03:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202607230003"
down_revision: str | None = "202607230002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add password and email verification fields to users."""
    op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Remove password and email verification fields from users."""
    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "password_hash")

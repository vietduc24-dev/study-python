"""Add login sessions and user registrations.

Revision ID: 202607230002
Revises: 202607230001
Create Date: 2026-07-23 00:02:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202607230002"
down_revision: str | None = "202607230001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def id_column() -> sa.Column:
    """Return the UUID primary key column."""
    return sa.Column("id", sa.Uuid(), nullable=False)


def timestamps() -> list[sa.Column]:
    """Return common timestamp columns."""
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    """Create auth session and registration tables."""
    op.create_table(
        "login_sessions",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("access_token_hash", sa.Text(), nullable=False),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.Text(), nullable=True),
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refresh_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_login_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_login_sessions")),
    )
    op.create_index(
        "uq_login_sessions_access_token_hash",
        "login_sessions",
        ["access_token_hash"],
        unique=True,
    )
    op.create_index(
        "uq_login_sessions_refresh_token_hash",
        "login_sessions",
        ["refresh_token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_login_sessions_user_active",
        "login_sessions",
        ["user_id", "refresh_expires_at"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    op.create_table(
        "user_registrations",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("verification_token_hash", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_registrations_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_registrations")),
    )
    op.create_index(
        "uq_user_registrations_email_pending",
        "user_registrations",
        ["email"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_index(
        "uq_user_registrations_verification_token_hash",
        "user_registrations",
        ["verification_token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_user_registrations_status_expires",
        "user_registrations",
        ["status", "expires_at"],
    )


def downgrade() -> None:
    """Drop auth session and registration tables."""
    op.drop_index(
        "ix_user_registrations_status_expires",
        table_name="user_registrations",
    )
    op.drop_index(
        "uq_user_registrations_verification_token_hash",
        table_name="user_registrations",
    )
    op.drop_index(
        "uq_user_registrations_email_pending",
        table_name="user_registrations",
    )
    op.drop_table("user_registrations")
    op.drop_index("ix_login_sessions_user_active", table_name="login_sessions")
    op.drop_index(
        "uq_login_sessions_refresh_token_hash",
        table_name="login_sessions",
    )
    op.drop_index(
        "uq_login_sessions_access_token_hash",
        table_name="login_sessions",
    )
    op.drop_table("login_sessions")

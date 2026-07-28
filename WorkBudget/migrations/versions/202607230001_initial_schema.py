"""Create initial WorkBudget schema.

Revision ID: 202607230001
Revises:
Create Date: 2026-07-23 00:01:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202607230001"
down_revision: str | None = None
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


def soft_delete() -> sa.Column:
    """Return the soft-delete column."""
    return sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)


def upgrade() -> None:
    """Create application tables, constraints, and indexes."""
    op.create_table(
        "users",
        id_column(),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("default_currency", sa.CHAR(length=3), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False),
        *timestamps(),
        soft_delete(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(
        "uq_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "groups",
        id_column(),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_currency", sa.CHAR(length=3), nullable=False),
        *timestamps(),
        soft_delete(),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=op.f("fk_groups_owner_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
    )

    op.create_table(
        "group_members",
        id_column(),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_group_members_group_id_groups"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_group_members_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group_members")),
    )
    op.create_index(
        "uq_group_members_group_user",
        "group_members",
        ["group_id", "user_id"],
        unique=True,
    )
    op.create_index("ix_group_members_user_id", "group_members", ["user_id"])

    op.create_table(
        "categories",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("group_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), nullable=True),
        sa.Column("icon", sa.Text(), nullable=True),
        *timestamps(),
        soft_delete(),
        sa.CheckConstraint(
            "(user_id IS NOT NULL AND group_id IS NULL) OR "
            "(user_id IS NULL AND group_id IS NOT NULL)",
            name=op.f("ck_categories_category_has_exactly_one_owner"),
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_categories_group_id_groups"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_categories_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
    )
    op.create_index(
        "uq_categories_user_name_active",
        "categories",
        ["user_id", "name"],
        unique=True,
        postgresql_where=sa.text("group_id IS NULL AND deleted_at IS NULL"),
    )
    op.create_index(
        "uq_categories_group_name_active",
        "categories",
        ["group_id", "name"],
        unique=True,
        postgresql_where=sa.text("user_id IS NULL AND deleted_at IS NULL"),
    )

    op.create_table(
        "expenses",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.CHAR(length=3), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.Text(), nullable=True),
        *timestamps(),
        soft_delete(),
        sa.CheckConstraint(
            "amount_minor > 0",
            name=op.f("ck_expenses_expense_amount_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_expenses_category_id_categories"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_expenses_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_expenses")),
    )
    op.create_index(
        "ix_expenses_user_date",
        "expenses",
        ["user_id", sa.text("expense_date DESC")],
    )
    op.create_index("ix_expenses_category_id", "expenses", ["category_id"])

    op.create_table(
        "personal_budgets",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("limit_amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.CHAR(length=3), nullable=False),
        sa.Column("period", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        *timestamps(),
        soft_delete(),
        sa.CheckConstraint(
            "limit_amount_minor > 0",
            name=op.f("ck_personal_budgets_personal_budget_limit_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_personal_budgets_category_id_categories"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_personal_budgets_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_personal_budgets")),
    )
    op.create_index(
        "ix_personal_budgets_user_period_dates",
        "personal_budgets",
        ["user_id", "period", "start_date", "end_date"],
    )

    op.create_table(
        "personal_tasks",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        soft_delete(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_personal_tasks_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_personal_tasks")),
    )
    op.create_index(
        "ix_personal_tasks_user_status_due",
        "personal_tasks",
        ["user_id", "status", "due_date"],
    )

    op.create_table(
        "group_schedules",
        id_column(),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("repeat_rule", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        *timestamps(),
        soft_delete(),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_group_schedules_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group_schedules")),
    )
    op.create_index(
        "ix_group_schedules_group_start",
        "group_schedules",
        ["group_id", "start_time"],
    )

    op.create_table(
        "schedule_assignees",
        id_column(),
        sa.Column("schedule_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["group_schedules.id"],
            name=op.f("fk_schedule_assignees_schedule_id_group_schedules"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_schedule_assignees_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_schedule_assignees")),
    )
    op.create_index(
        "uq_schedule_assignees_schedule_user",
        "schedule_assignees",
        ["schedule_id", "user_id"],
        unique=True,
    )
    op.create_index(
        "ix_schedule_assignees_user_id",
        "schedule_assignees",
        ["user_id"],
    )

    op.create_table(
        "group_tasks",
        id_column(),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        soft_delete(),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_group_tasks_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group_tasks")),
    )
    op.create_index(
        "ix_group_tasks_group_status_due",
        "group_tasks",
        ["group_id", "status", "due_date"],
    )

    op.create_table(
        "task_assignees",
        id_column(),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["group_tasks.id"],
            name=op.f("fk_task_assignees_task_id_group_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_task_assignees_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_assignees")),
    )
    op.create_index(
        "uq_task_assignees_task_user",
        "task_assignees",
        ["task_id", "user_id"],
        unique=True,
    )
    op.create_index("ix_task_assignees_user_id", "task_assignees", ["user_id"])

    op.create_table(
        "shared_expenses",
        id_column(),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("paid_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.CHAR(length=3), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        *timestamps(),
        soft_delete(),
        sa.CheckConstraint(
            "amount_minor > 0",
            name=op.f("ck_shared_expenses_shared_expense_amount_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_shared_expenses_category_id_categories"),
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_shared_expenses_group_id_groups"),
        ),
        sa.ForeignKeyConstraint(
            ["paid_by_user_id"],
            ["users.id"],
            name=op.f("fk_shared_expenses_paid_by_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shared_expenses")),
    )
    op.create_index(
        "ix_shared_expenses_group_date",
        "shared_expenses",
        ["group_id", sa.text("expense_date DESC")],
    )
    op.create_index(
        "ix_shared_expenses_paid_by_user_id",
        "shared_expenses",
        ["paid_by_user_id"],
    )

    op.create_table(
        "reminders",
        id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("personal_task_id", sa.Uuid(), nullable=True),
        sa.Column("group_task_id", sa.Uuid(), nullable=True),
        sa.Column("schedule_id", sa.Uuid(), nullable=True),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.CheckConstraint(
            "num_nonnulls(personal_task_id, group_task_id, schedule_id) = 1",
            name=op.f("ck_reminders_reminder_has_exactly_one_target"),
        ),
        sa.ForeignKeyConstraint(
            ["group_task_id"],
            ["group_tasks.id"],
            name=op.f("fk_reminders_group_task_id_group_tasks"),
        ),
        sa.ForeignKeyConstraint(
            ["personal_task_id"],
            ["personal_tasks.id"],
            name=op.f("fk_reminders_personal_task_id_personal_tasks"),
        ),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["group_schedules.id"],
            name=op.f("fk_reminders_schedule_id_group_schedules"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_reminders_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reminders")),
    )
    op.create_index(
        "ix_reminders_user_pending_remind_at",
        "reminders",
        ["user_id", "remind_at"],
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    """Drop application tables in reverse dependency order."""
    op.drop_index("ix_reminders_user_pending_remind_at", table_name="reminders")
    op.drop_table("reminders")
    op.drop_index("ix_shared_expenses_paid_by_user_id", table_name="shared_expenses")
    op.drop_index("ix_shared_expenses_group_date", table_name="shared_expenses")
    op.drop_table("shared_expenses")
    op.drop_index("ix_task_assignees_user_id", table_name="task_assignees")
    op.drop_index("uq_task_assignees_task_user", table_name="task_assignees")
    op.drop_table("task_assignees")
    op.drop_index("ix_group_tasks_group_status_due", table_name="group_tasks")
    op.drop_table("group_tasks")
    op.drop_index("ix_schedule_assignees_user_id", table_name="schedule_assignees")
    op.drop_index(
        "uq_schedule_assignees_schedule_user",
        table_name="schedule_assignees",
    )
    op.drop_table("schedule_assignees")
    op.drop_index("ix_group_schedules_group_start", table_name="group_schedules")
    op.drop_table("group_schedules")
    op.drop_index("ix_personal_tasks_user_status_due", table_name="personal_tasks")
    op.drop_table("personal_tasks")
    op.drop_index(
        "ix_personal_budgets_user_period_dates",
        table_name="personal_budgets",
    )
    op.drop_table("personal_budgets")
    op.drop_index("ix_expenses_category_id", table_name="expenses")
    op.drop_index("ix_expenses_user_date", table_name="expenses")
    op.drop_table("expenses")
    op.drop_index("uq_categories_group_name_active", table_name="categories")
    op.drop_index("uq_categories_user_name_active", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_group_members_user_id", table_name="group_members")
    op.drop_index("uq_group_members_group_user", table_name="group_members")
    op.drop_table("group_members")
    op.drop_table("groups")
    op.drop_index("uq_users_email_active", table_name="users")
    op.drop_table("users")

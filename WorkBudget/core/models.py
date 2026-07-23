"""Compatibility exports for SQLAlchemy models.

New code should import models from their owning module, for example
`WorkBudget.modules.users.model.User`.
"""

from WorkBudget.modules.auth.model import LoginSession, UserRegistration
from WorkBudget.modules.budget.model import PersonalBudget
from WorkBudget.modules.finance.model import Category, Expense, SharedExpense
from WorkBudget.modules.notifications.model import Reminder
from WorkBudget.modules.tasks.model import (
    GroupSchedule,
    GroupTask,
    PersonalTask,
    ScheduleAssignee,
    TaskAssignee,
)
from WorkBudget.modules.users.model import User
from WorkBudget.modules.workspace.model import Group, GroupMember

__all__ = [
    "Category",
    "Expense",
    "Group",
    "GroupMember",
    "GroupSchedule",
    "GroupTask",
    "LoginSession",
    "PersonalBudget",
    "PersonalTask",
    "Reminder",
    "ScheduleAssignee",
    "SharedExpense",
    "TaskAssignee",
    "User",
    "UserRegistration",
]

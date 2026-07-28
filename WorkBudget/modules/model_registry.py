"""Import all SQLAlchemy models so Alembic can discover metadata."""

import WorkBudget.modules.auth.model  # noqa: F401
import WorkBudget.modules.budget.model  # noqa: F401
import WorkBudget.modules.finance.model  # noqa: F401
import WorkBudget.modules.notifications.model  # noqa: F401
import WorkBudget.modules.tasks.model  # noqa: F401
import WorkBudget.modules.users.model  # noqa: F401
import WorkBudget.modules.workspace.model  # noqa: F401

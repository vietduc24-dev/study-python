"""Application configuration."""

from functools import lru_cache
import os
from pathlib import Path

from pydantic import BaseModel


def load_env_file(path: Path | None = None) -> None:
    """Load simple KEY=VALUE pairs from WorkBudget/.env."""
    env_path = path or Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Settings(BaseModel):
    """Runtime settings loaded by the application."""

    app_name: str = "WorkBudget API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://workbudget:workbudget@postgres:5432/workbudget"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    load_env_file()
    return Settings(
        app_name=os.getenv("APP_NAME", "WorkBudget API"),
        environment=os.getenv("ENVIRONMENT", "development"),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://workbudget:workbudget@postgres:5432/workbudget",
        ),
    )

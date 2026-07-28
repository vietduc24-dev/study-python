"""Application configuration."""

from functools import lru_cache
import os
from pathlib import Path
from urllib.parse import quote_plus

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


def get_database_url() -> str:
    """Return DATABASE_URL or compose it from split DB environment values."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    if db_host and db_name and db_user and db_password:
        db_port = os.getenv("DB_PORT", "5432")
        return (
            "postgresql+psycopg://"
            f"{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
        )

    return "postgresql+psycopg://workbudget:workbudget@postgres:5432/workbudget"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    load_env_file()
    return Settings(
        app_name=os.getenv("APP_NAME", "WorkBudget API"),
        environment=os.getenv("ENVIRONMENT", "development"),
        database_url=get_database_url(),
    )

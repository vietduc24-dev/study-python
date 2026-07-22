"""Application configuration."""

from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime settings loaded by the application."""

    app_name: str = "WorkBudget API"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


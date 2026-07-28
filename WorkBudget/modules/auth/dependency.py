"""Auth module dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from WorkBudget.core.database import get_db_session
from WorkBudget.modules.auth.service import AuthService
from WorkBudget.modules.users.model import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
) -> User:
    """Return the currently authenticated user."""
    return AuthService(session).get_user_for_access_token(credentials.credentials)

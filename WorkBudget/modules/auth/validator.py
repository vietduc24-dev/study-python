"""Auth validation helpers."""

from datetime import datetime

from fastapi import HTTPException, status

from WorkBudget.core.security import verify_password
from WorkBudget.modules.auth.model import LoginSession, UserRegistration
from WorkBudget.modules.users.model import User


class AuthValidator:
    """Business validation rules for auth workflows."""

    @staticmethod
    def ensure_email_available(existing_user: User | None) -> None:
        """Ensure a registration email is not already used."""
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

    @staticmethod
    def ensure_registration_active(
        registration: UserRegistration | None,
        now: datetime,
    ) -> UserRegistration:
        """Ensure a registration token exists and has not expired."""
        if registration is None or registration.expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )
        return registration

    @staticmethod
    def ensure_registration_user_exists(user: User | None) -> User:
        """Ensure the pending registration still belongs to an existing user."""
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration user does not exist",
            )
        return user

    @staticmethod
    def ensure_valid_login_credentials(user: User | None, password: str) -> User:
        """Ensure login credentials match an active user."""
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return user

    @staticmethod
    def ensure_email_verified(user: User) -> None:
        """Ensure a user verified their email before login."""
        if user.email_verified_at is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not verified",
            )

    @staticmethod
    def ensure_refresh_session_active(
        login_session: LoginSession | None,
        now: datetime,
    ) -> LoginSession:
        """Ensure a refresh token maps to an active session."""
        if login_session is None or login_session.refresh_expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        return login_session

    @staticmethod
    def ensure_access_session_active(
        login_session: LoginSession | None,
        now: datetime,
    ) -> LoginSession:
        """Ensure an access token maps to an active session."""
        if login_session is None or login_session.access_expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return login_session

    @staticmethod
    def ensure_access_user_exists(user: User | None) -> User:
        """Ensure an access-token session still belongs to an existing user."""
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

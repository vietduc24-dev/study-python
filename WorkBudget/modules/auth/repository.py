"""Auth data access."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from WorkBudget.modules.auth.model import LoginSession, UserRegistration
from WorkBudget.modules.users.model import User


class AuthRepository:
    """Data access for auth workflows."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_active_user_by_email(self, email: str) -> User | None:
        """Return a non-deleted user by email."""
        statement = select(User).where(User.email == email, User.deleted_at.is_(None))
        return self.session.execute(statement).scalar_one_or_none()

    def get_user_by_id(self, user_id: UUID) -> User | None:
        """Return a non-deleted user by id."""
        statement = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        return self.session.execute(statement).scalar_one_or_none()

    def create_user(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        default_currency: str,
        timezone: str,
    ) -> User:
        """Create a user."""
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            default_currency=default_currency,
            timezone=timezone,
        )
        self.session.add(user)
        self.session.flush()
        return user

    def create_registration(
        self,
        *,
        user: User,
        verification_token_hash: str,
        expires_at: datetime,
    ) -> UserRegistration:
        """Create a pending registration row."""
        registration = UserRegistration(
            user_id=user.id,
            email=user.email,
            name=user.name,
            verification_token_hash=verification_token_hash,
            status="pending",
            expires_at=expires_at,
        )
        self.session.add(registration)
        self.session.flush()
        return registration

    def get_pending_registration(
        self, *, email: str, verification_token_hash: str
    ) -> UserRegistration | None:
        """Return a pending registration by email and token hash."""
        statement = select(UserRegistration).where(
            UserRegistration.email == email,
            UserRegistration.verification_token_hash == verification_token_hash,
            UserRegistration.status == "pending",
        )
        return self.session.execute(statement).scalar_one_or_none()

    def create_login_session(
        self,
        *,
        user: User,
        access_token_hash: str,
        refresh_token_hash: str,
        access_expires_at: datetime,
        refresh_expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> LoginSession:
        """Create a login session."""
        login_session = LoginSession(
            user_id=user.id,
            access_token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(login_session)
        self.session.flush()
        return login_session

    def get_active_session_by_access_token_hash(
        self, access_token_hash: str
    ) -> LoginSession | None:
        """Return an active session by access token hash."""
        statement = select(LoginSession).where(
            LoginSession.access_token_hash == access_token_hash,
            LoginSession.revoked_at.is_(None),
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_active_session_by_refresh_token_hash(
        self, refresh_token_hash: str
    ) -> LoginSession | None:
        """Return an active session by refresh token hash."""
        statement = select(LoginSession).where(
            LoginSession.refresh_token_hash == refresh_token_hash,
            LoginSession.revoked_at.is_(None),
        )
        return self.session.execute(statement).scalar_one_or_none()

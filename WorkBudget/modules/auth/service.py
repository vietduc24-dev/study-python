"""Auth business logic."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from WorkBudget.core.security import (
    generate_token,
    hash_password,
    hash_token,
)
from WorkBudget.modules.auth.repository import AuthRepository
from WorkBudget.modules.auth.schema import (
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerifyRegistrationRequest,
    VerifyRegistrationResponse,
)
from WorkBudget.modules.auth.validator import AuthValidator
from WorkBudget.modules.users.model import User

ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=30)
REGISTRATION_TOKEN_TTL = timedelta(hours=24)


@dataclass(frozen=True)
class RequestContext:
    """Request metadata stored with login sessions."""

    user_agent: str | None
    ip_address: str | None


class AuthService:
    """Auth workflow service."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AuthRepository(session)

    def register(self, request: RegisterRequest) -> RegisterResponse:
        """Create a user and pending registration."""
        existing_user = self.repository.get_active_user_by_email(request.email)
        AuthValidator.ensure_email_available(existing_user)

        verification_token = generate_token()
        expires_at = datetime.now(UTC) + REGISTRATION_TOKEN_TTL
        user = self.repository.create_user(
            name=request.name.strip(),
            email=request.email,
            password_hash=hash_password(request.password),
            default_currency=request.default_currency,
            timezone=request.timezone.strip(),
        )
        registration = self.repository.create_registration(
            user=user,
            verification_token_hash=hash_token(verification_token),
            expires_at=expires_at,
        )
        self.session.commit()
        return RegisterResponse(
            user_id=user.id,
            registration_id=registration.id,
            status=registration.status,
            verification_token=verification_token,
            expires_at=expires_at,
        )

    def verify_registration(
        self, request: VerifyRegistrationRequest
    ) -> VerifyRegistrationResponse:
        """Verify a pending registration token."""
        now = datetime.now(UTC)
        registration = self.repository.get_pending_registration(
            email=request.email,
            verification_token_hash=hash_token(request.verification_token),
        )
        registration = AuthValidator.ensure_registration_active(registration, now)

        user = AuthValidator.ensure_registration_user_exists(
            self.repository.get_user_by_id(registration.user_id)
        )

        user.email_verified_at = now
        user.updated_at = now
        registration.status = "verified"
        registration.verified_at = now
        registration.updated_at = now
        self.session.commit()
        return VerifyRegistrationResponse(
            user_id=user.id,
            status=registration.status,
            email_verified_at=now,
        )

    def login(self, request: LoginRequest, context: RequestContext) -> TokenResponse:
        """Authenticate a user and create tokens."""
        user = AuthValidator.ensure_valid_login_credentials(
            self.repository.get_active_user_by_email(request.email),
            request.password,
        )
        AuthValidator.ensure_email_verified(user)
        return self._create_tokens_for_user(user=user, context=context)

    def refresh(self, refresh_token: str, context: RequestContext) -> TokenResponse:
        """Rotate tokens using an active refresh token."""
        now = datetime.now(UTC)
        login_session = self.repository.get_active_session_by_refresh_token_hash(
            hash_token(refresh_token)
        )
        login_session = AuthValidator.ensure_refresh_session_active(login_session, now)

        access_token = generate_token()
        new_refresh_token = generate_token()
        access_expires_at = now + ACCESS_TOKEN_TTL
        refresh_expires_at = now + REFRESH_TOKEN_TTL

        login_session.access_token_hash = hash_token(access_token)
        login_session.refresh_token_hash = hash_token(new_refresh_token)
        login_session.access_expires_at = access_expires_at
        login_session.refresh_expires_at = refresh_expires_at
        login_session.user_agent = context.user_agent
        login_session.ip_address = context.ip_address
        login_session.last_used_at = now
        login_session.updated_at = now
        self.session.commit()
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

    def logout(self, refresh_token: str) -> LogoutResponse:
        """Revoke a login session."""
        now = datetime.now(UTC)
        login_session = self.repository.get_active_session_by_refresh_token_hash(
            hash_token(refresh_token)
        )
        if login_session is None:
            return LogoutResponse(revoked=False)

        login_session.revoked_at = now
        login_session.updated_at = now
        self.session.commit()
        return LogoutResponse(revoked=True)

    def get_user_for_access_token(self, access_token: str) -> User:
        """Return current user for a valid access token."""
        now = datetime.now(UTC)
        login_session = self.repository.get_active_session_by_access_token_hash(
            hash_token(access_token)
        )
        login_session = AuthValidator.ensure_access_session_active(login_session, now)

        user = AuthValidator.ensure_access_user_exists(
            self.repository.get_user_by_id(login_session.user_id)
        )

        login_session.last_used_at = now
        login_session.updated_at = now
        self.session.commit()
        return user

    def _create_tokens_for_user(
        self, *, user: User, context: RequestContext
    ) -> TokenResponse:
        """Create and persist a token pair."""
        now = datetime.now(UTC)
        access_token = generate_token()
        refresh_token = generate_token()
        access_expires_at = now + ACCESS_TOKEN_TTL
        refresh_expires_at = now + REFRESH_TOKEN_TTL
        self.repository.create_login_session(
            user=user,
            access_token_hash=hash_token(access_token),
            refresh_token_hash=hash_token(refresh_token),
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
            user_agent=context.user_agent,
            ip_address=context.ip_address,
        )
        self.session.commit()
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

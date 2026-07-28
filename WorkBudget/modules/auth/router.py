"""Auth API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from WorkBudget.common.response import ApiResponse
from WorkBudget.core.database import get_db_session
from WorkBudget.modules.auth.dependency import get_current_user
from WorkBudget.modules.auth.schema import (
    CurrentUserResponse,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerifyRegistrationRequest,
    VerifyRegistrationResponse,
)
from WorkBudget.modules.auth.service import AuthService, RequestContext
from WorkBudget.modules.users.model import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def build_request_context(request: Request) -> RequestContext:
    """Build request metadata for session tracking."""
    return RequestContext(
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post(
    "/register",
    response_model=ApiResponse[RegisterResponse],
    status_code=201,
    response_model_exclude_none=True,
)
def register(
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    """Create a pending user registration."""
    return ApiResponse.success(
        AuthService(session).register(payload),
        message="Registration created",
    )


@router.post(
    "/verify-registration",
    response_model=ApiResponse[VerifyRegistrationResponse],
    response_model_exclude_none=True,
)
def verify_registration(
    payload: VerifyRegistrationRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    """Verify a registration token."""
    return ApiResponse.success(
        AuthService(session).verify_registration(payload),
        message="Registration verified",
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    response_model_exclude_none=True,
)
def login(
    payload: LoginRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    """Login and create token session."""
    return ApiResponse.success(
        AuthService(session).login(payload, build_request_context(request)),
        message="Login successful",
    )


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    response_model_exclude_none=True,
)
def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    """Rotate access and refresh tokens."""
    return ApiResponse.success(
        AuthService(session).refresh(
            payload.refresh_token,
            build_request_context(request),
        ),
        message="Token refreshed",
    )


@router.post(
    "/logout",
    response_model=ApiResponse[LogoutResponse],
    response_model_exclude_none=True,
)
def logout(
    payload: LogoutRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    """Revoke a refresh token session."""
    return ApiResponse.success(
        AuthService(session).logout(payload.refresh_token),
        message="Logout completed",
    )


@router.get(
    "/me",
    response_model=ApiResponse[CurrentUserResponse],
    response_model_exclude_none=True,
)
def me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict[str, object]:
    """Return current authenticated user."""
    return ApiResponse.success(current_user)

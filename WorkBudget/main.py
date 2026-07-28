"""FastAPI application entrypoint."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from WorkBudget.common.response import ApiResponse
from WorkBudget.modules.auth.router import router as auth_router

app = FastAPI(title="WorkBudget API")
app.include_router(auth_router)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    """Return HTTP errors using the standard API envelope."""
    detail = exc.detail
    message = detail if isinstance(detail, str) else "Request failed"
    errors = {"detail": detail}
    return ApiResponse.error_response(
        status_code=exc.status_code,
        message=message,
        errors=errors,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return validation errors using the standard API envelope."""
    return ApiResponse.error_response(
        status_code=422,
        message="Validation error",
        errors={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    """Return unhandled errors using the standard API envelope."""
    return ApiResponse.error_response(
        status_code=500,
        message="Internal server error",
        errors={"detail": "Internal server error"},
    )


@app.get(
    "/health",
    response_model=ApiResponse[dict[str, str]],
    response_model_exclude_none=True,
)
def health_check() -> dict[str, object]:
    """Return a simple health status for container and local checks."""
    return ApiResponse.success({"status": "ok"})

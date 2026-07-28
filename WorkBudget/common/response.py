"""Shared API response helpers."""

from typing import Any, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse

DataT = TypeVar("DataT")


class ApiResponseSchema[DataT](BaseModel):
    """Standard API response envelope for frontend clients."""

    success: bool
    message: str
    data: DataT | None = None
    errors: dict[str, Any] | None = None


class ApiResponse:
    """Factory helpers for standard API responses."""

    def __class_getitem__(cls, item: Any) -> type[ApiResponseSchema[Any]]:
        """Allow `response_model=ApiResponse[SomeSchema]` in routers."""
        return ApiResponseSchema[item]

    @staticmethod
    def success[DataT](
        data: DataT | None = None,
        message: str = "Success",
    ) -> dict[str, Any]:
        """Build a successful API response envelope."""
        return {
            "success": True,
            "message": message,
            "data": data,
        }

    @staticmethod
    def error_response(
        *,
        status_code: int,
        message: str,
        errors: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JSONResponse:
        """Build a JSON error response envelope."""
        payload = ApiResponse.error(message, errors)
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(payload),
            headers=headers,
        )

    @staticmethod
    def error(
        message: str,
        errors: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build an error API response envelope."""
        return {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors or {"detail": message},
        }

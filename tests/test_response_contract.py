"""API response contract tests."""

from fastapi.testclient import TestClient

from WorkBudget.main import app


def test_validation_error_uses_standard_envelope() -> None:
    """Request validation errors use the frontend response contract."""
    client = TestClient(app)

    response = client.post("/api/v1/auth/register", json={})

    body = response.json()
    assert response.status_code == 422
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["data"] is None
    assert isinstance(body["errors"]["detail"], list)

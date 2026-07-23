"""Health endpoint tests."""

from fastapi.testclient import TestClient

from WorkBudget.main import app


def test_health_check() -> None:
    """Health endpoint returns an ok status."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

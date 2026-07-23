"""FastAPI application entrypoint."""

from fastapi import FastAPI

app = FastAPI(title="WorkBudget API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health status for container and local checks."""
    return {"status": "ok"}


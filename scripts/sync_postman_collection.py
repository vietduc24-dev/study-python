"""Sync the generated Postman collection to Postman via the Postman API."""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

POSTMAN_API_URL = "https://api.getpostman.com"
ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_COLLECTION_PATH = (
    ROOT_DIR / "docs" / "postman" / "workbudget.postman_collection.json"
)
DEFAULT_ENV_PATH = ROOT_DIR / "WorkBudget" / ".env"


def load_env_file(path: Path = DEFAULT_ENV_PATH) -> None:
    """Load simple KEY=VALUE pairs, letting Postman file values override env."""
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_key = key.strip()
        env_value = value.strip().strip('"').strip("'")
        if env_key.startswith("POSTMAN_"):
            os.environ[env_key] = env_value
        else:
            os.environ.setdefault(env_key, env_value)


def env_enabled(name: str) -> bool:
    """Return true when an environment flag is enabled."""
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def required_env(name: str) -> str:
    """Read a required env value without leaking it in errors."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_collection(path: Path) -> dict[str, Any]:
    """Load the generated Postman collection."""
    if not path.exists():
        raise RuntimeError(f"Postman collection does not exist: {path}")
    with path.open() as file:
        return json.load(file)


def sync_collection(path: Path = DEFAULT_COLLECTION_PATH) -> dict[str, Any]:
    """Replace the configured Postman collection with the local collection."""
    load_env_file()
    api_key = required_env("POSTMAN_API_KEY")
    collection_id = required_env("POSTMAN_COLLECTION_ID")
    collection = load_collection(path)

    request_body = json.dumps({"collection": collection}).encode()
    request = urllib.request.Request(
        f"{POSTMAN_API_URL}/collections/{collection_id}",
        data=request_body,
        method="PUT",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"Postman sync failed with HTTP {exc.code}: {body[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Postman sync failed: {exc.reason}") from exc

    return json.loads(payload)


def main() -> None:
    """Sync generated Postman collection when enabled."""
    load_env_file()
    if not env_enabled("POSTMAN_SYNC_ENABLED"):
        print("Postman sync skipped: POSTMAN_SYNC_ENABLED is not true")
        return

    result = sync_collection()
    collection = result.get("collection", {})
    name = collection.get("name", "unknown")
    uid = collection.get("uid") or collection.get("id") or "unknown"
    print(f"Synced Postman collection: {name} ({uid})")


if __name__ == "__main__":
    main()

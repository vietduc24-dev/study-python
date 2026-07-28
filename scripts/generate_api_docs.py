"""Generate OpenAPI and Postman artifacts from the FastAPI app."""

import json
import os
from pathlib import Path
from typing import Any

from WorkBudget.main import app

ROOT_DIR = Path(__file__).resolve().parents[1]
OPENAPI_PATH = ROOT_DIR / "docs" / "api" / "openapi.json"
POSTMAN_PATH = ROOT_DIR / "docs" / "postman" / "workbudget.postman_collection.json"


def build_raw_body(operation: dict[str, Any]) -> dict[str, Any] | None:
    """Build a Postman raw JSON body from an OpenAPI requestBody."""
    request_body = operation.get("requestBody")
    if not request_body:
        return None

    content = request_body.get("content", {})
    if "application/json" not in content:
        return None

    schema = content["application/json"].get("schema", {})
    example = content["application/json"].get("example")
    if example is None:
        example = example_from_schema(schema)

    return {
        "mode": "raw",
        "raw": json.dumps(example, indent=2),
        "options": {"raw": {"language": "json"}},
    }


def example_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Create a lightweight example payload from an OpenAPI schema."""
    ref = schema.get("$ref")
    if ref:
        schema_name = ref.rsplit("/", 1)[-1]
        schema = app.openapi()["components"]["schemas"].get(schema_name, {})

    properties = schema.get("properties", {})
    example: dict[str, Any] = {}
    for name, metadata in properties.items():
        if "default" in metadata:
            example[name] = metadata["default"]
        elif metadata.get("format") == "email" or name == "email":
            example[name] = "user@example.com"
        elif name == "verification_token":
            example[name] = "{{verification_token}}"
        elif name == "access_token":
            example[name] = "{{access_token}}"
        elif name == "refresh_token":
            example[name] = "{{refresh_token}}"
        elif "token" in name:
            example[name] = f"{{{{{name}}}}}"
        elif name == "password":
            example[name] = "StrongPass123"
        elif metadata.get("type") == "integer":
            example[name] = 1
        elif metadata.get("type") == "boolean":
            example[name] = True
        else:
            example[name] = f"example_{name}"
    return example


def build_postman_collection(openapi: dict[str, Any]) -> dict[str, Any]:
    """Build a Postman collection from an OpenAPI document."""
    folders: dict[str, list[dict[str, Any]]] = {}
    for path, methods in sorted(openapi["paths"].items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue

            tags = operation.get("tags") or ["default"]
            folder_name = str(tags[0])
            request: dict[str, Any] = {
                "method": method.upper(),
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "url": {
                    "raw": "{{base_url}}" + path,
                    "host": ["{{base_url}}"],
                    "path": [part for part in path.strip("/").split("/") if part],
                },
                "description": operation.get("description")
                or operation.get("summary", ""),
            }

            body = build_raw_body(operation)
            if body is not None:
                request["body"] = body

            security = operation.get("security")
            if security:
                request["auth"] = {
                    "type": "bearer",
                    "bearer": [{"key": "token", "value": "{{access_token}}"}],
                }

            item = {
                "name": operation.get("summary") or operation.get("operationId"),
                "request": request,
                "response": [],
            }
            events = build_postman_events(path)
            if events:
                item["event"] = events
            folders.setdefault(folder_name, []).append(item)

    return {
        "info": {
            "name": "WorkBudget API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {"name": folder_name, "item": items}
            for folder_name, items in sorted(folders.items())
        ],
        "variable": [
            {"key": "base_url", "value": "http://127.0.0.1:8000"},
            {"key": "access_token", "value": ""},
            {"key": "refresh_token", "value": ""},
            {"key": "verification_token", "value": ""},
        ],
    }


def build_postman_events(path: str) -> list[dict[str, Any]]:
    """Add token capture scripts for auth endpoints."""
    if path.endswith("/register"):
        script = [
            "const body = pm.response.json();",
            "const data = body.data || body;",
            "if (data.verification_token) {",
            "  pm.collectionVariables.set(",
            '    "verification_token",',
            "    data.verification_token,",
            "  );",
            "}",
        ]
    elif path.endswith("/login") or path.endswith("/refresh"):
        script = [
            "const body = pm.response.json();",
            "const data = body.data || body;",
            "if (data.access_token) {",
            '  pm.collectionVariables.set("access_token", data.access_token);',
            "}",
            "if (data.refresh_token) {",
            '  pm.collectionVariables.set("refresh_token", data.refresh_token);',
            "}",
        ]
    else:
        return []

    return [{"listen": "test", "script": {"type": "text/javascript", "exec": script}}]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write formatted JSON to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    """Generate docs artifacts."""
    openapi = app.openapi()
    write_json(OPENAPI_PATH, openapi)
    write_json(POSTMAN_PATH, build_postman_collection(openapi))
    print(f"Wrote {OPENAPI_PATH}")
    print(f"Wrote {POSTMAN_PATH}")

    if os.getenv("POSTMAN_SYNC_ENABLED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        from scripts.sync_postman_collection import sync_collection

        result = sync_collection(POSTMAN_PATH)
        collection = result.get("collection", {})
        name = collection.get("name", "unknown")
        uid = collection.get("uid") or collection.get("id") or "unknown"
        print(f"Synced Postman collection: {name} ({uid})")


if __name__ == "__main__":
    main()

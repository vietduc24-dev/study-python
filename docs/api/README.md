# API Docs

Generated from the FastAPI application.

When adding an API in any module, define the FastAPI route with:

- `tags=["module_name"]` so Postman groups requests by module.
- `summary` and `description` so OpenAPI and Postman are readable.
- `response_model` so response schemas are exported.

```bash
docker compose -f docker/docker-compose.local.yml exec dev-workbudget-app python scripts/generate_api_docs.py
```

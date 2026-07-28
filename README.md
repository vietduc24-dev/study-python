# WorkBudget backend

FastAPI backend for the WorkBudget screen catalog. The API reads
`WorkBudget_Danh_muc_man_hinh.xlsx` as the catalog source of truth.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
uvicorn WorkBudget.main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Docker

Runtime values such as ports are defined in `WorkBudget/.env.local` or
`WorkBudget/.env.dev`.

```bash
docker compose -f docker/docker-compose.local.yml up --build
```

Use the dev compose file when you want dev-specific env values:

```bash
docker compose -f docker/docker-compose.dev.yml up --build
```

## Auth API

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/verify-registration`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

## API Documentation

Regenerate OpenAPI and Postman files after adding or changing routes:

```bash
docker compose -f docker/docker-compose.local.yml exec dev-workbudget-app python scripts/generate_api_docs.py
```

Outputs:

- `docs/api/openapi.json`
- `docs/postman/workbudget.postman_collection.json`

For every new module API, add route `tags`, `summary`, `description`, and
`response_model`. The generator uses tags as Postman folders.

If `POSTMAN_SYNC_ENABLED=true`, the generator also syncs
`docs/postman/workbudget.postman_collection.json` to the collection configured
by `POSTMAN_COLLECTION_ID`.
{
    "success": false,
    "message": "",
    "errors": {
        "detail": ""
    }
}
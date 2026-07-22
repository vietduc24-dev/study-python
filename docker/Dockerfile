FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

WORKDIR /app

FROM base AS dev

COPY pyproject.toml README.md ./
COPY WorkBudget ./WorkBudget
RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE ${APP_PORT}
CMD ["sh", "-c", "uvicorn WorkBudget.main:app --host ${APP_HOST} --port ${APP_PORT} --reload"]

FROM base AS production

RUN groupadd --system app && useradd --system --gid app app
COPY pyproject.toml README.md ./
COPY WorkBudget ./WorkBudget
RUN pip install --no-cache-dir . && chown -R app:app /app

USER app
EXPOSE ${APP_PORT}
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.getenv('APP_PORT', '8000')}/health\")"
CMD ["sh", "-c", "uvicorn WorkBudget.main:app --host ${APP_HOST} --port ${APP_PORT}"]

# syntax=docker/dockerfile:1

# --- base: python + uv, no project code -------------------------------------
FROM python:3.12-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:0.11.3 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

# --- deps-prod: runtime dependencies only -----------------------------------
FROM base AS deps-prod

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- deps-dev: runtime + dev tooling ---------------------------------------
FROM deps-prod AS deps-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --extra dev --no-install-project

# --- dev: source is bind-mounted by compose, venv lives outside /app -------
FROM deps-dev AS dev

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- runtime: minimal production image -------------------------------------
FROM deps-prod AS runtime

ENV APP_ENV=production \
    LOG_FORMAT=json \
    HF_HOME=/data/hf-cache

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN useradd --system --uid 10001 --create-home appuser \
    && mkdir -p /data/uploads /data/hf-cache \
    && chown -R appuser:appuser /data

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

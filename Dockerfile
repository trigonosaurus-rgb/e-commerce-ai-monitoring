# Rivalscope: one image = API + scheduler + Telegram bot + the built web app.
#   docker build -t rivalscope .
#   docker run -p 8000:8000 --env-file .env -v rivalscope-data:/app/data rivalscope

# --- 1. Build the frontend into static files ------------------------------------------
FROM node:24.21.0-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- 2. Python runtime ----------------------------------------------------------------
FROM python:3.14.8-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1
WORKDIR /app

# dependencies first: this layer is reused until pyproject.toml / uv.lock change
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY backend/ backend/
COPY --from=frontend /app/frontend/out frontend/out

RUN useradd --create-home --uid 1000 app && mkdir -p data && chown app data
USER app

ENV PATH="/app/.venv/bin:$PATH" \
    DATABASE_URL=sqlite:////app/data/rivalscope.db \
    FORWARDED_ALLOW_IPS="*"
VOLUME /app/data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"

# a single process on purpose: the price scheduler and the Telegram bot run inside it
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

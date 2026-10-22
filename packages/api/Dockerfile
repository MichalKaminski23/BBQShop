# Obraz API budowany z katalogu głównego repo:
#   docker build -f packages/api/Dockerfile .
FROM ghcr.io/astral-sh/uv:0.13.1-python3.13-trixie-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Najpierw same zależności – warstwa cache'uje się, dopóki nie zmieni się uv.lock.
COPY pyproject.toml uv.lock .python-version ./
COPY packages/core/pyproject.toml packages/core/
COPY packages/db/pyproject.toml packages/db/
COPY packages/api/pyproject.toml packages/api/
COPY packages/sqli/pyproject.toml packages/sqli/
COPY packages/nosqli/pyproject.toml packages/nosqli/
RUN uv sync --locked --no-dev --no-install-workspace

COPY packages ./packages
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    BBQ_HOST=0.0.0.0 \
    BBQ_PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "alembic -c packages/db/alembic.ini upgrade head && bbq-api"]

FROM ghcr.io/astral-sh/uv:0.13.1-python3.13-trixie-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
COPY packages/core/pyproject.toml packages/core/
COPY packages/db/pyproject.toml packages/db/
COPY packages/api/pyproject.toml packages/api/
COPY packages/concurrency/pyproject.toml packages/concurrency/
COPY packages/sqli/pyproject.toml packages/sqli/
COPY packages/nosqli/pyproject.toml packages/nosqli/
COPY packages/nplusone/pyproject.toml packages/nplusone/
RUN uv sync --locked --no-dev --no-install-workspace

COPY packages ./packages
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    BBQ_HOST=0.0.0.0 \
    BBQ_PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "alembic -c packages/db/alembic.ini upgrade head && bbq-api"]

"""Uruchomienie serwera: ``uv run bbq-api`` lub ``python -m bbq_api``."""

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "bbq_api.app:create_app",
        factory=True,
        host=os.getenv("BBQ_HOST", "127.0.0.1"),
        port=int(os.getenv("BBQ_PORT", "8000")),
        reload=os.getenv("BBQ_RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()

"""Fabryka aplikacji FastAPI."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bbq_api import system
from bbq_api.registry import ActiveModule, discover_modules, resolve_modules
from bbq_core.config import Settings, get_settings
from bbq_core.db import create_engine, create_mongo_client, create_session_factory
from bbq_core.module import BBQModule

logger = logging.getLogger("bbq_api")

API_PREFIX = "/api"


def create_app(settings: Settings | None = None, modules: list[BBQModule] | None = None) -> FastAPI:
    """Tworzy aplikację i montuje routery włączonych modułów.

    Args:
        settings: Ustawienia; domyślnie wczytywane z ``.env``.
        modules: Lista modułów; domyślnie odkrywana przez entry points.
    """
    settings = settings or get_settings()
    active = resolve_modules(discover_modules() if modules is None else modules, settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(settings.postgres_dsn)
        mongo_client = create_mongo_client(settings.mongo_uri)
        app.state.session_factory = create_session_factory(engine)
        app.state.mongo_db = mongo_client[settings.mongo_db]
        try:
            if settings.seed_on_startup:
                await _seed(app, active)
            yield
        finally:
            await mongo_client.close()
            await engine.dispose()

    app = FastAPI(title="BBQShop", version="0.1.0", lifespan=lifespan)
    app.state.modules = active
    app.include_router(system.router, prefix=API_PREFIX)

    for item in active:
        if item.enabled:
            app.include_router(item.module.build_router(item.variant), prefix=API_PREFIX)
        logger.info("Moduł %s: %s", item.module.name, item.variant)

    return app


async def _seed(app: FastAPI, active: list[ActiveModule]) -> None:
    """Wypełnia bazę danymi przykładowymi włączonych modułów."""
    async with app.state.session_factory() as session:
        for item in active:
            if item.enabled and item.module.seed is not None:
                await item.module.seed(session)
        await session.commit()

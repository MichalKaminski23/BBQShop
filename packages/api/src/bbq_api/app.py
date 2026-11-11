"""Fabryka aplikacji FastAPI."""

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from bbq_api import system
from bbq_api.registry import discover_modules, resolve_modules
from bbq_core.config import Settings, get_settings
from bbq_core.db import (
    begin_query_metrics,
    create_engine,
    create_mongo_client,
    create_session_factory,
    end_query_metrics,
)
from bbq_core.module import BBQModule
from bbq_db.seed import seed_mongo, seed_postgres

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
        engine = create_engine(settings.postgres_dsn, enable_metrics=settings.db_metrics)
        mongo_client = create_mongo_client(settings.mongo_uri)
        app.state.session_factory = create_session_factory(engine)
        app.state.mongo_db = mongo_client[settings.mongo_db]
        try:
            if settings.seed_on_startup:
                await _seed(app)
            yield
        finally:
            await mongo_client.close()
            await engine.dispose()

    app = FastAPI(title="BBQShop", version="0.1.0", lifespan=lifespan)
    app.state.modules = active

    @app.middleware("http")
    async def add_query_metrics(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not settings.db_metrics:
            return await call_next(request)

        metrics, token = begin_query_metrics()
        try:
            response = await call_next(request)
        finally:
            end_query_metrics(token)
        response.headers["X-SQL-Query-Count"] = str(metrics.count)
        response.headers["X-SQL-Query-Time-Ms"] = f"{metrics.elapsed_ms:.2f}"
        return response

    app.include_router(system.router, prefix=API_PREFIX)

    for item in active:
        if item.enabled:
            app.include_router(item.module.build_router(item.variant), prefix=API_PREFIX)
        logger.info("Moduł %s: %s", item.module.name, item.variant)

    return app


async def _seed(app: FastAPI) -> None:
    """Wypełnia obie bazy danymi przykładowymi (tylko puste tabele i kolekcje)."""
    async with app.state.session_factory() as session:
        await seed_postgres(session)
        await session.commit()
    await seed_mongo(app.state.mongo_db)

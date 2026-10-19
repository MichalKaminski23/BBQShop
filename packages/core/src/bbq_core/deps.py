"""Zależności FastAPI współdzielone przez moduły.

Zasoby (pula Postgresa, klient Mongo) są tworzone raz w ``lifespan`` aplikacji
i trzymane w ``app.state``; moduły pobierają je przez ``Depends``.
"""

from collections.abc import AsyncIterator
from typing import Annotated, cast

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Sesja PostgreSQL na czas jednego żądania."""
    factory = cast(async_sessionmaker[AsyncSession], request.app.state.session_factory)
    async with factory() as session:
        yield session


def get_mongo_db(request: Request) -> AsyncDatabase[dict[str, object]]:
    """Baza MongoDB aplikacji."""
    return cast(AsyncDatabase[dict[str, object]], request.app.state.mongo_db)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
MongoDep = Annotated[AsyncDatabase[dict[str, object]], Depends(get_mongo_db)]

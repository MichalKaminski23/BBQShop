"""✅ Wersja POPRAWIONA.

- Fraza trafia do bazy jako parametr zapytania, nigdy jako fragment SQL.
- Znaki specjalne ``LIKE`` (``%``, ``_``) są escapowane, więc są traktowane dosłownie.
- Długość frazy jest ograniczona na poziomie endpointu (``MAX_QUERY_LENGTH``).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_sqli.models import Product
from bbq_sqli.schemas import ProductOut

MAX_QUERY_LENGTH = 100
_LIKE_ESCAPE = "\\"


def escape_like(value: str) -> str:
    """Escapuje znaki specjalne wzorca ``LIKE``."""
    for char in (_LIKE_ESCAPE, "%", "_"):
        value = value.replace(char, _LIKE_ESCAPE + char)
    return value


class SecureProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, query: str) -> list[ProductOut]:
        pattern = f"%{escape_like(query)}%"
        stmt = (
            select(Product)
            .where(Product.name.ilike(pattern, escape=_LIKE_ESCAPE))
            .order_by(Product.id)
        )
        products = await self._session.scalars(stmt)
        return [ProductOut.model_validate(product) for product in products]

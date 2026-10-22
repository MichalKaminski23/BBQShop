"""Wersja PODATNA – celowo, w celach edukacyjnych.

Fraza wyszukiwania jest wklejana bezpośrednio w treść zapytania SQL.
Apostrof w ``query`` kończy literał tekstowy, a reszta frazy staje się częścią
zapytania – np. ``UNION SELECT`` pozwala odczytać dowolną tabelę.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from bbq_sqli.schemas import ProductOut


class VulnerableProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, query: str) -> list[ProductOut]:
        sql = (
            "SELECT id, name, category, price, description FROM products "
            f"WHERE name ILIKE '%{query}%' ORDER BY id"
        )
        connection = await self._session.connection()
        result = await connection.exec_driver_sql(sql)
        return [ProductOut.model_validate(row) for row in result.mappings()]

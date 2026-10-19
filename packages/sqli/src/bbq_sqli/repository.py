"""Wspólny interfejs obu wariantów wyszukiwarki."""

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from bbq_sqli.schemas import ProductOut


class ProductRepository(Protocol):
    def __init__(self, session: AsyncSession) -> None: ...

    async def search(self, query: str) -> list[ProductOut]:
        """Zwraca produkty, których nazwa zawiera ``query`` (bez rozróżniania wielkości liter)."""
        ...

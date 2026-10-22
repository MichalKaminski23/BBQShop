"""Wspólny interfejs obu wariantów logowania."""

from typing import Protocol

from pymongo.asynchronous.collection import AsyncCollection


class UserRepository(Protocol):
    def __init__(self, users: AsyncCollection[dict[str, object]]) -> None: ...

    async def authenticate(self, username: object, password: object) -> dict[str, object] | None:
        """Zwraca dokument użytkownika po poprawnym logowaniu, w przeciwnym razie ``None``."""
        ...

"""✅ Wersja POPRAWIONA.

- Login i hasło muszą być tekstem; obiekty (operatory Mongo) są odrzucane,
  więc do filtra nigdy nie trafi operator zapytania.
- Filtr zawiera wyłącznie nazwę użytkownika; hasło jest weryfikowane osobno
  przez porównanie hashy w czasie stałym (``verify_password``).
- Dodatkowo endpoint wymusza typy przez model Pydantic (nie-tekst → 422).
"""

from pymongo.asynchronous.collection import AsyncCollection

from bbq_db.mongo import verify_password


class SecureUserRepository:
    def __init__(self, users: AsyncCollection[dict[str, object]]) -> None:
        self._users = users

    async def authenticate(self, username: object, password: object) -> dict[str, object] | None:
        # ✅ Odrzucamy wszystko, co nie jest tekstem – operator Mongo nigdy nie trafi do filtra.
        if not isinstance(username, str) or not isinstance(password, str):
            return None

        user = await self._users.find_one({"username": username})
        if user is None:
            return None

        if verify_password(password, str(user["password_hash"])):
            return user
        return None

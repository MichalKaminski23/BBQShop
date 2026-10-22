"""Wersja PODATNA – celowo, w celach edukacyjnych.

Login i hasło pochodzą z surowego JSON i trafiają wprost do filtra zapytania
MongoDB. Gdy atakujący poda wartość będącą obiektem (np. ``{"$ne": null}``),
staje się ona operatorem zapytania, a nie zwykłym napisem – pozwala to pominąć
weryfikację i zalogować się bez znajomości danych.
"""

from pymongo.asynchronous.collection import AsyncCollection

from bbq_db.mongo import verify_password


class VulnerableUserRepository:
    def __init__(self, users: AsyncCollection[dict[str, object]]) -> None:
        self._users = users

    async def authenticate(self, username: object, password: object) -> dict[str, object] | None:
        # username trafia wprost do filtra – można wstrzyknąć operator Mongo ({"$ne": null}).
        user = await self._users.find_one({"username": username})
        if user is None:
            return None

        if isinstance(password, str):
            # Zwykłe logowanie: weryfikacja hasła.
            if verify_password(password, str(user["password_hash"])):
                return user
            return None

        # Hasło nie jest tekstem: zamiast weryfikować hash, "sprawdzamy" je
        # operatorem w zapytaniu – dowolny operator (np. {"$ne": null}) pasuje.
        match = await self._users.find_one(
            {"username": user["username"], "password_hash": password}
        )
        return user if match is not None else None

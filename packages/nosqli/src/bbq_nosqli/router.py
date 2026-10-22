"""Endpointy modułu NoSQLi – implementacja zależy od wariantu z ``.env``."""

from fastapi import APIRouter, HTTPException, Request, status
from pymongo.asynchronous.database import AsyncDatabase

from bbq_core.deps import MongoDep
from bbq_core.module import Variant
from bbq_db.mongo import USERS_COLLECTION
from bbq_nosqli.repository import UserRepository
from bbq_nosqli.schemas import LoginOut, LoginRequest
from bbq_nosqli.secure import SecureUserRepository
from bbq_nosqli.vulnerable import VulnerableUserRepository

REPOSITORIES: dict[Variant, type[UserRepository]] = {
    Variant.VULNERABLE: VulnerableUserRepository,
    Variant.SECURE: SecureUserRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]

    router = APIRouter(prefix="/login", tags=["nosqli"])

    async def _login(
        mongo: AsyncDatabase[dict[str, object]], username: object, password: object
    ) -> LoginOut:
        user = await repository_cls(mongo[USERS_COLLECTION]).authenticate(username, password)
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Nieprawidłowy login lub hasło")
        return LoginOut(username=str(user["username"]), role=str(user["role"]))

    if variant is Variant.SECURE:

        @router.post("")
        async def login_secure(mongo: MongoDep, credentials: LoginRequest) -> LoginOut:
            """Loguje użytkownika (dane wymuszone jako tekst przez model Pydantic)."""
            return await _login(mongo, credentials.username, credentials.password)
    else:

        @router.post("")
        async def login_vulnerable(mongo: MongoDep, request: Request) -> LoginOut:
            """Loguje użytkownika, przyjmując surowy JSON (podatne na NoSQLi)."""
            try:
                body = await request.json()
            except ValueError:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Niepoprawny JSON") from None
            if not isinstance(body, dict):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Oczekiwano obiektu JSON")
            # Operatory Mongo nadal trafiają wprost do zapytania – podatność działa.
            return await _login(mongo, body.get("username"), body.get("password"))

    return router

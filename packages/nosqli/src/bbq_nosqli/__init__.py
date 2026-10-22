"""NoSQL Injection w logowaniu (MongoDB)."""

from bbq_core.module import BBQModule
from bbq_nosqli.router import build_router

module = BBQModule(
    name="nosqli",
    title="NoSQL Injection",
    description="Logowanie sklejające filtr zapytania MongoDB z danych użytkownika.",
    build_router=build_router,
)

__all__ = ["module"]

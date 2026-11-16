"""SQL Injection w wyszukiwarce produktów."""

from bbq_core.module import BBQModule
from bbq_sqli.router import build_router

module = BBQModule(
    name="sqli",
    title="SQL Injection",
    description="Wyszukiwarka produktów sklejająca zapytanie SQL z danych użytkownika.",
    build_router=build_router,
)

__all__ = ["module"]

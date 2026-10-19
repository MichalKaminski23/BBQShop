"""SQL Injection w wyszukiwarce produktów."""

from bbq_core.module import BBQModule
from bbq_sqli.router import build_router
from bbq_sqli.seed import seed

module = BBQModule(
    name="sqli",
    title="SQL Injection",
    description="Wyszukiwarka produktów sklejająca zapytanie SQL z danych użytkownika.",
    build_router=build_router,
    seed=seed,
)

__all__ = ["module"]

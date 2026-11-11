"""Problem N+1 przy pobieraniu zamówień i ich pozycji."""

from bbq_core.module import BBQModule
from bbq_nplusone.router import build_router

module = BBQModule(
    name="nplusone",
    title="Problem N+1",
    description="Lista zamówień pobierająca pozycje osobnym zapytaniem dla każdego zamówienia.",
    build_router=build_router,
)

__all__ = ["module"]

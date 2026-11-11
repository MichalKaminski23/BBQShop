"""Nieograniczona współbieżność i wielokrotne wykonanie zamówienia."""

from bbq_concurrency.router import build_router
from bbq_core.module import BBQModule

module = BBQModule(
    name="concurrency",
    title="Nieograniczona współbieżność",
    description="Składanie tego samego zamówienia wielokrotnie bez idempotencji i limitu operacji.",
    build_router=build_router,
)

__all__ = ["module"]

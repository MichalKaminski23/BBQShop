"""Race condition przy wykorzystaniu kuponu rabatowego."""

from bbq_core.module import BBQModule
from bbq_race.router import build_router

module = BBQModule(
    name="race",
    title="Race Conditions",
    description="Równoczesne wykorzystanie jednorazowego kuponu rabatowego.",
    build_router=build_router,
)

__all__ = ["module"]

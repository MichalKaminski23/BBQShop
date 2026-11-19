"""Niepoprawne zarządzanie deskryptorami plików i gniazd."""

from bbq_core.module import BBQModule
from bbq_fdleak.router import build_router

module = BBQModule(
    name="fdleak",
    title="Deskryptory plików i gniazd",
    description="Demonstracja utrzymywania otwartych plików i gniazd zamiast ich zamykania.",
    build_router=build_router,
)

__all__ = ["module"]

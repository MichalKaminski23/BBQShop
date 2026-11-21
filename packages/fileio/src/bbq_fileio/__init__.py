"""Arbitrary file read/write: odczyt i zapis plików po nazwie od użytkownika."""

from bbq_core.module import BBQModule
from bbq_fileio.router import build_router

module = BBQModule(
    name="fileio",
    title="Arbitrary File Read/Write",
    description="Odczyt i zapis plików po nazwie podanej wprost przez użytkownika.",
    build_router=build_router,
)

__all__ = ["module"]

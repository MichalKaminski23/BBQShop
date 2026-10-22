"""Kontrakt, który spełnia każdy moduł podatności.

Moduł rejestruje się przez entry point w grupie ``bbqshop.modules``::

    [project.entry-points."bbqshop.modules"]
    sqli = "bbq_sqli:module"
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from fastapi import APIRouter

ENTRY_POINT_GROUP = "bbqshop.modules"


class Variant(StrEnum):
    """Wariant modułu wybierany w ``.env``."""

    VULNERABLE = "vulnerable"
    SECURE = "secure"
    OFF = "off"


type RouterFactory = Callable[[Variant], APIRouter]


@dataclass(frozen=True, slots=True, kw_only=True)
class BBQModule:
    """Opis modułu podatności.

    Attributes:
        name: Krótki identyfikator (np. ``sqli``), używany w zmiennej ``BBQ_MODULE_<NAME>``.
        title: Nazwa wyświetlana we frontendzie.
        description: Krótki opis podatności.
        build_router: Tworzy router FastAPI dla wybranego wariantu
            (wywoływane tylko dla ``vulnerable`` i ``secure``).
    """

    name: str
    title: str
    description: str
    build_router: RouterFactory

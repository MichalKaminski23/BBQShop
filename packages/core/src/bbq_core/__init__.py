"""Wspólne elementy BBQShop: konfiguracja, połączenia z bazami i kontrakt modułu."""

from bbq_core.config import Settings, get_settings
from bbq_core.module import BBQModule, Variant

__all__ = ["BBQModule", "Settings", "Variant", "get_settings"]

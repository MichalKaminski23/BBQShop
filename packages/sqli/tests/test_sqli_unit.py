"""Testy jednostkowe modułu SQLi (bez bazy danych)."""

from bbq_core.module import Variant
from bbq_sqli.router import REPOSITORIES
from bbq_sqli.secure import SecureProductRepository, escape_like
from bbq_sqli.vulnerable import VulnerableProductRepository


def test_escape_like() -> None:
    assert escape_like(r"50%_off\x") == r"50\%\_off\\x"


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableProductRepository
    assert REPOSITORIES[Variant.SECURE] is SecureProductRepository

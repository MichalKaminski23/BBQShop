"""Testy jednostkowe modułu N+1 (bez bazy danych)."""

from bbq_core.module import Variant
from bbq_nplusone.router import REPOSITORIES
from bbq_nplusone.secure import SecureOrderRepository
from bbq_nplusone.vulnerable import VulnerableOrderRepository


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableOrderRepository
    assert REPOSITORIES[Variant.SECURE] is SecureOrderRepository

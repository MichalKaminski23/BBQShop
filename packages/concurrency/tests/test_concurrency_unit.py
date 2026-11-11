"""Testy jednostkowe modułu współbieżności."""

from bbq_concurrency.router import REPOSITORIES
from bbq_concurrency.secure import SecureOrderRepository
from bbq_concurrency.vulnerable import VulnerableOrderRepository
from bbq_core.module import Variant


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableOrderRepository
    assert REPOSITORIES[Variant.SECURE] is SecureOrderRepository

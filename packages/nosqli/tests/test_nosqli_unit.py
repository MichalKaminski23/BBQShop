"""Testy jednostkowe modułu NoSQLi (bez bazy danych)."""

from bbq_core.module import Variant
from bbq_nosqli.router import REPOSITORIES
from bbq_nosqli.secure import SecureUserRepository
from bbq_nosqli.vulnerable import VulnerableUserRepository


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableUserRepository
    assert REPOSITORIES[Variant.SECURE] is SecureUserRepository

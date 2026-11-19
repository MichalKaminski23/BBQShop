"""Testy struktury i wyboru wariantu modułu fdleak."""

from bbq_core.module import Variant
from bbq_fdleak.router import REPOSITORIES
from bbq_fdleak.secure import SecureResourceRepository
from bbq_fdleak.vulnerable import VulnerableResourceRepository


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableResourceRepository
    assert REPOSITORIES[Variant.SECURE] is SecureResourceRepository

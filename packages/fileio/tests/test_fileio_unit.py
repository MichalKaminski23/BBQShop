"""Test jednostkowy: wybór repozytorium wg wariantu."""

from bbq_core.module import Variant
from bbq_fileio.router import REPOSITORIES
from bbq_fileio.secure import SecureFileRepository
from bbq_fileio.vulnerable import VulnerableFileRepository


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableFileRepository
    assert REPOSITORIES[Variant.SECURE] is SecureFileRepository

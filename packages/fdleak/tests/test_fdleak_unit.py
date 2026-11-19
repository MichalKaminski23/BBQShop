"""Testy struktury i wyboru wariantu modułu fdleak."""

from bbq_core.module import Variant
from bbq_fdleak.router import REPOSITORIES
from bbq_fdleak.secure import SecureResourceRepository
from bbq_fdleak.secure.repository import SecureResourceRepository as SecureRepository
from bbq_fdleak.vulnerable import VulnerableResourceRepository
from bbq_fdleak.vulnerable.repository import VulnerableResourceRepository as Repository


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableResourceRepository
    assert REPOSITORIES[Variant.SECURE] is SecureResourceRepository


def test_vulnerable_file_leaves_resources_open() -> None:
    repository = Repository()
    try:
        result = repository.open_file(3)

        assert result.resource_type == "file"
        assert result.opened_count == 3
        assert result.closed_count == 0
        assert result.outstanding_count == 3
        assert len(repository._open_files) == 3
    finally:
        repository.close_all()


def test_vulnerable_socket_leaves_resources_open() -> None:
    repository = Repository()
    try:
        result = repository.open_socket(3)

        assert result.resource_type == "socket"
        assert result.opened_count == 3
        assert result.closed_count == 0
        assert result.outstanding_count == 3
        assert len(repository._open_sockets) == 6
    finally:
        repository.close_all()


def test_secure_file_closes_resources() -> None:
    repository = SecureRepository()

    result = repository.open_file(3)

    assert result.resource_type == "file"
    assert result.opened_count == 3
    assert result.closed_count == 3
    assert result.outstanding_count == 0


def test_secure_socket_closes_resources() -> None:
    repository = SecureRepository()

    result = repository.open_socket(3)

    assert result.resource_type == "socket"
    assert result.opened_count == 3
    assert result.closed_count == 3
    assert result.outstanding_count == 0

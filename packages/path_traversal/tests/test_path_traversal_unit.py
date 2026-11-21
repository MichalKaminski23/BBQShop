"""Testy jednostkowe wariantów modułu Path Traversal."""

from pathlib import Path

import pytest

from bbq_core.module import Variant
from bbq_path_traversal.router import REPOSITORIES
from bbq_path_traversal.secure import SecureFileRepository
from bbq_path_traversal.secure.repository import SecureFileRepository as SecureRepository
from bbq_path_traversal.vulnerable import VulnerableFileRepository
from bbq_path_traversal.vulnerable.repository import (
    VulnerableFileRepository as VulnerableRepository,
)


def test_variant_selects_repository() -> None:
    assert REPOSITORIES[Variant.VULNERABLE] is VulnerableFileRepository
    assert REPOSITORIES[Variant.SECURE] is SecureFileRepository


def test_vulnerable_repository_allows_parent_directory(tmp_path: Path) -> None:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("sekret", encoding="utf-8")

    repository = VulnerableRepository(base_dir)

    assert repository.path("../secret.txt") == base_dir / "../secret.txt"
    assert repository.read("../secret.txt") == "sekret"


def test_vulnerable_repository_allows_absolute_path(tmp_path: Path) -> None:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("sekret", encoding="utf-8")

    repository = VulnerableRepository(base_dir)

    assert repository.path(str(secret)) == secret
    assert repository.read(str(secret)) == "sekret"


def test_secure_repository_rejects_parent_directory(tmp_path: Path) -> None:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("sekret", encoding="utf-8")

    repository = SecureRepository(base_dir)

    with pytest.raises(ValueError, match="wychodzi poza"):
        repository.path("../secret.txt")


def test_secure_repository_rejects_absolute_path(tmp_path: Path) -> None:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("sekret", encoding="utf-8")

    repository = SecureRepository(base_dir)

    with pytest.raises(ValueError, match="wychodzi poza"):
        repository.path(str(secret))


def test_secure_repository_reads_file_inside_base_directory(tmp_path: Path) -> None:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    (base_dir / "grill.txt").write_text("instrukcja", encoding="utf-8")

    repository = SecureRepository(base_dir)

    assert repository.path("grill.txt") == (base_dir / "grill.txt").resolve()
    assert repository.read("grill.txt") == "instrukcja"


def test_secure_repository_rejects_symlink_outside_base_directory(tmp_path: Path) -> None:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("sekret", encoding="utf-8")
    try:
        (base_dir / "link.txt").symlink_to(secret)
    except OSError as exc:
        pytest.skip(f"Tworzenie dowiązań symbolicznych niedostępne: {exc}")

    repository = SecureRepository(base_dir)

    with pytest.raises(ValueError, match="wychodzi poza"):
        repository.path("link.txt")

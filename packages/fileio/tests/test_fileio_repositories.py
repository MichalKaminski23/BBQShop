"""Te same scenariusze na obu wariantach File I/O (operują na plikach, bez Dockera)."""

from pathlib import Path

import pytest

from bbq_fileio.repository import FileRepository
from bbq_fileio.secure import SecureFileRepository
from bbq_fileio.storage import SAMPLE_NAME, SECRET_CONTENT, SECRET_NAME, prepare
from bbq_fileio.vulnerable import VulnerableFileRepository

BOTH = pytest.mark.parametrize(
    "repository_cls",
    [VulnerableFileRepository, SecureFileRepository],
    ids=["vulnerable", "secure"],
)


@pytest.fixture
def base(tmp_path: Path) -> Path:
    return prepare(tmp_path)


@BOTH
def test_read_allowed_file(base: Path, repository_cls: type[FileRepository]) -> None:
    assert "grill" in repository_cls(base).read(SAMPLE_NAME).content.lower()


@BOTH
def test_write_then_read_in_base(base: Path, repository_cls: type[FileRepository]) -> None:
    result = repository_cls(base).write("notatka.txt", "test")

    assert result.written == 4
    assert (base / "notatka.txt").read_text(encoding="utf-8") == "test"


def test_vulnerable_read_escapes_to_secret(base: Path) -> None:
    result = VulnerableFileRepository(base).read(f"../{SECRET_NAME}")

    assert result.content == SECRET_CONTENT


def test_secure_read_blocks_escape(base: Path) -> None:
    with pytest.raises(PermissionError):
        SecureFileRepository(base).read(f"../{SECRET_NAME}")


def test_vulnerable_write_escapes_base(base: Path) -> None:
    VulnerableFileRepository(base).write("../pwned.txt", "x")

    assert (base.parent / "pwned.txt").exists()


def test_secure_write_blocks_escape(base: Path) -> None:
    with pytest.raises(PermissionError):
        SecureFileRepository(base).write("../pwned.txt", "x")

    assert not (base.parent / "pwned.txt").exists()

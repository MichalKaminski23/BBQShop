"""Wspólny interfejs obu wariantów."""

from pathlib import Path
from typing import Protocol

from bbq_fileio.schemas import FileContent, WriteResult


class FileRepository(Protocol):
    def __init__(self, base: Path) -> None: ...

    def read(self, name: str) -> FileContent:
        """Odczytuje plik ``name``."""
        ...

    def write(self, name: str, content: str) -> WriteResult:
        """Zapisuje ``content`` do pliku ``name``."""
        ...

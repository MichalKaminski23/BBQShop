"""Wspólny interfejs obu wariantów odczytu plików."""

from pathlib import Path
from typing import Protocol


class FileRepository(Protocol):
    def __init__(self, base_dir: Path) -> None: ...

    def path(self, file_path: str) -> Path:
        """Zwraca ścieżkę do pliku wskazanego przez użytkownika."""
        ...

    def read(self, file_path: str) -> str:
        """Zwraca treść pliku wskazanego przez użytkownika."""
        ...

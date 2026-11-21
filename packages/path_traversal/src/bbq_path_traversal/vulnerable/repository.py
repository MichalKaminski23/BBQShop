"""Wersja PODATNA - celowo, w celach edukacyjnych."""

from pathlib import Path


class VulnerableFileRepository:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir

    def path(self, file_path: str) -> Path:
        """Zwraca ścieżkę bez sprawdzenia, czy pozostaje w katalogu bazowym."""
        return self._base_dir / file_path

    def read(self, file_path: str) -> str:
        """Odczytuje plik bez sprawdzenia, czy pozostaje w katalogu bazowym."""
        return self.path(file_path).read_text(encoding="utf-8")

"""Wersja POPRAWIONA."""

from pathlib import Path


class SecureFileRepository:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir.resolve()

    def path(self, file_path: str) -> Path:
        """Zwraca plik tylko wtedy, gdy ścieżka pozostaje w katalogu bazowym."""
        candidate = (self._base_dir / file_path).resolve()
        if candidate != self._base_dir and self._base_dir not in candidate.parents:
            raise ValueError("Ścieżka wychodzi poza katalog bazowy")
        return candidate

    def read(self, file_path: str) -> str:
        """Odczytuje plik tylko wtedy, gdy ścieżka pozostaje w katalogu bazowym."""
        return self.path(file_path).read_text(encoding="utf-8")

"""Wersja PODATNA - nazwa pliku od użytkownika trafia wprost do ścieżki.

``base / name`` nie ogranicza nazwy: ``../secret.txt`` wychodzi poza katalog
dozwolony, a ścieżka bezwzględna (np. ``/etc/passwd``) całkiem go pomija.
Dotyczy to tak samo odczytu, jak i zapisu.
"""

from pathlib import Path

from bbq_fileio.schemas import FileContent, WriteResult


class VulnerableFileRepository:
    def __init__(self, base: Path) -> None:
        self._base = base

    def read(self, name: str) -> FileContent:
        content = (self._base / name).read_text(encoding="utf-8")
        return FileContent(name=name, content=content)

    def write(self, name: str, content: str) -> WriteResult:
        (self._base / name).write_text(content, encoding="utf-8")
        return WriteResult(name=name, written=len(content))

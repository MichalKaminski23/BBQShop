"""Wersja POPRAWIONA - ścieżka jest zawężona do katalogu dozwolonego.

Po złożeniu i rozwinięciu ścieżki (``resolve``) sprawdzamy, że nadal leży
wewnątrz katalogu bazowego. Odrzuca to ``../`` oraz ścieżki bezwzględne,
więc odczyt i zapis nie wyjdą poza katalog dozwolony.
"""

from pathlib import Path

from bbq_fileio.schemas import FileContent, WriteResult


class SecureFileRepository:
    def __init__(self, base: Path) -> None:
        self._base = base.resolve()

    def _safe_path(self, name: str) -> Path:
        path = (self._base / name).resolve()
        if not path.is_relative_to(self._base):
            raise PermissionError("Ścieżka poza dozwolonym katalogiem")
        return path

    def read(self, name: str) -> FileContent:
        content = self._safe_path(name).read_text(encoding="utf-8")
        return FileContent(name=name, content=content)

    def write(self, name: str, content: str) -> WriteResult:
        self._safe_path(name).write_text(content, encoding="utf-8")
        return WriteResult(name=name, written=len(content))

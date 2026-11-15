"""Katalog plików modułu i dane demonstracyjne.

Układ: ``<root>/files/`` to katalog dozwolony (tam leżą pliki produktów),
a ``<root>/secret.txt`` to cel ataku położony **obok** niego. Dzięki temu
``../secret.txt`` (albo ścieżka bezwzględna) wychodzi poza katalog dozwolony.
"""

import os
from pathlib import Path

ALLOWED_DIRNAME = "files"
SAMPLE_NAME = "manual.txt"
SAMPLE_CONTENT = "Instrukcja grilla: rozpal, poczekaj na żar, grilluj.\n"
SECRET_NAME = "secret.txt"  # noqa: S105  (nazwa pliku demonstracyjnego, nie hasło)
SECRET_CONTENT = "FLAG{arbitrary_file_read_write}\n"  # noqa: S105  (fikcyjny sekret demo)


def default_root() -> Path:
    """Katalog roboczy modułu (konfigurowalny przez ``BBQ_FILEIO_DIR``)."""
    return Path(os.getenv("BBQ_FILEIO_DIR", "fileio-data")).resolve()


def prepare(root: Path) -> Path:
    """Tworzy katalog dozwolony i dane demonstracyjne; zwraca ten katalog."""
    base = root / ALLOWED_DIRNAME
    base.mkdir(parents=True, exist_ok=True)
    (base / SAMPLE_NAME).write_text(SAMPLE_CONTENT, encoding="utf-8")
    (root / SECRET_NAME).write_text(SECRET_CONTENT, encoding="utf-8")
    return base

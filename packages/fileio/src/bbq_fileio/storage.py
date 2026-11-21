"""Katalog instrukcji produktów i dane demonstracyjne.

Każdy produkt ma plik instrukcji ``manual-<id>.txt`` w katalogu dozwolonym
``<root>/files/``. Obok niego (``<root>/secret.txt``) leży cel ataku, więc
``../secret.txt`` albo ścieżka bezwzględna wychodzi poza katalog instrukcji.
"""

import os
from pathlib import Path

ALLOWED_DIRNAME = "files"
# Identyfikatory produktów ze wspólnego seedu (bbq_db ma 7 produktów: 1..7).
PRODUCT_IDS = range(1, 8)
SECRET_NAME = "secret.txt"  # noqa: S105  (nazwa pliku demonstracyjnego, nie hasło)
SECRET_CONTENT = "FLAG{arbitrary_file_read_write}\n"  # noqa: S105  (fikcyjny sekret demo)


def manual_name(product_id: int) -> str:
    """Nazwa pliku instrukcji dla produktu."""
    return f"manual-{product_id}.txt"


def _manual_content(product_id: int) -> str:
    return (
        f"Instrukcja produktu #{product_id}\n"
        "1. Rozpalanie: użyj rozpałki, odczekaj na równy żar.\n"
        "2. Grillowanie: utrzymuj stałą temperaturę.\n"
        "3. Czyszczenie: wyczyść ruszt po ostygnięciu.\n"
    )


def default_root() -> Path:
    """Katalog roboczy modułu (konfigurowalny przez ``BBQ_FILEIO_DIR``)."""
    return Path(os.getenv("BBQ_FILEIO_DIR", "fileio-data")).resolve()


def prepare(root: Path) -> Path:
    """Tworzy katalog instrukcji i dane demonstracyjne; zwraca ten katalog."""
    base = root / ALLOWED_DIRNAME
    base.mkdir(parents=True, exist_ok=True)
    for product_id in PRODUCT_IDS:
        (base / manual_name(product_id)).write_text(_manual_content(product_id), encoding="utf-8")
    (root / SECRET_NAME).write_text(SECRET_CONTENT, encoding="utf-8")
    return base

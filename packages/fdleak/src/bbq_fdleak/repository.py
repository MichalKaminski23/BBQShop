"""Wspólny interfejs obu wariantów obsługi zasobów."""

from typing import Protocol

from bbq_fdleak.schemas import ResourceDemoResult


class ResourceRepository(Protocol):
    def open_file(self, count: int) -> ResourceDemoResult:
        """Uruchamia demonstrację otwierania plików."""
        ...

    def open_socket(self, count: int) -> ResourceDemoResult:
        """Uruchamia demonstrację otwierania gniazd."""
        ...

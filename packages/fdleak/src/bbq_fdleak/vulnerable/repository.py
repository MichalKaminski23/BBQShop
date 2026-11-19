"""Wersja PODATNA - zasoby pozostaja otwarte."""

import os
import socket
from typing import IO

from bbq_fdleak.schemas import ResourceDemoResult


class VulnerableResourceRepository:
    def __init__(self) -> None:
        self._open_files: list[IO[str]] = []
        self._open_sockets: list[socket.socket] = []

    def open_file(self, count: int) -> ResourceDemoResult:
        for _ in range(count):
            opened = open(os.devnull, "r", encoding="utf-8")
            self._open_files.append(opened)

        return ResourceDemoResult(
            resource_type="file",
            opened_count=count,
            closed_count=0,
        )

    def open_socket(self, count: int) -> ResourceDemoResult:
        for _ in range(count):
            opened = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._open_sockets.append(opened)

        return ResourceDemoResult(
            resource_type="socket",
            opened_count=count,
            closed_count=0,
        )

    def close_all(self) -> None:
        """Sprzatanie wyjatkowo potrzebne testom i restartom procesu demonstracyjnego."""
        for opened in self._open_files:
            opened.close()
        for opened in self._open_sockets:
            opened.close()
        self._open_files.clear()
        self._open_sockets.clear()

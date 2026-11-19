"""Wersja PODATNA - zasoby pozostaja otwarte."""

import os
import socket
from typing import IO

from bbq_fdleak.schemas import ResourceDemoResult


def create_local_tcp_connection() -> tuple[socket.socket, socket.socket]:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(listener.getsockname())
    server, _ = listener.accept()
    listener.close()
    client.sendall(b"bbq-fdleak-demo")
    server.recv(len(b"bbq-fdleak-demo"))
    return client, server


class VulnerableResourceRepository:
    def __init__(self) -> None:
        self._open_files: list[IO[str]] = []
        self._open_sockets: list[socket.socket] = []

    def open_file(self, count: int) -> ResourceDemoResult:
        for _ in range(count):
            opened = open(os.devnull, encoding="utf-8")  # noqa: SIM115
            self._open_files.append(opened)

        return ResourceDemoResult(
            resource_type="file",
            opened_count=count,
            closed_count=0,
            outstanding_count=len(self._open_files),
        )

    def open_socket(self, count: int) -> ResourceDemoResult:
        for _ in range(count):
            self._open_sockets.extend(create_local_tcp_connection())

        return ResourceDemoResult(
            resource_type="socket",
            opened_count=count,
            closed_count=0,
            outstanding_count=len(self._open_sockets) // 2,
        )

    def close_all(self) -> None:
        """Sprzatanie wyjatkowo potrzebne testom i restartom procesu demonstracyjnego."""
        for opened_file in self._open_files:
            opened_file.close()
        for opened_socket in self._open_sockets:
            opened_socket.close()
        self._open_files.clear()
        self._open_sockets.clear()

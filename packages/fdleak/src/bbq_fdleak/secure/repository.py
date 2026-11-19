"""Wersja POPRAWIONA - zasoby sa zamykane natychmiast."""

import os
import socket

from bbq_fdleak.schemas import ResourceDemoResult


class SecureResourceRepository:
    def open_file(self, count: int) -> ResourceDemoResult:
        closed_count = 0
        for _ in range(count):
            with open(os.devnull, "r", encoding="utf-8"):
                pass
            closed_count += 1

        return ResourceDemoResult(
            resource_type="file",
            opened_count=count,
            closed_count=closed_count,
        )

    def open_socket(self, count: int) -> ResourceDemoResult:
        closed_count = 0
        for _ in range(count):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM):
                pass
            closed_count += 1

        return ResourceDemoResult(
            resource_type="socket",
            opened_count=count,
            closed_count=closed_count,
        )

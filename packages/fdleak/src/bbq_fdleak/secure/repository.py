"""Wersja POPRAWIONA - zasoby sa zamykane natychmiast."""

import os

from bbq_fdleak.schemas import ResourceDemoResult
from bbq_fdleak.vulnerable.repository import create_local_tcp_connection


class SecureResourceRepository:
    def open_file(self, count: int) -> ResourceDemoResult:
        closed_count = 0
        for _ in range(count):
            with open(os.devnull, encoding="utf-8"):
                pass
            closed_count += 1

        return ResourceDemoResult(
            resource_type="file",
            opened_count=count,
            closed_count=closed_count,
            outstanding_count=0,
        )

    def open_socket(self, count: int) -> ResourceDemoResult:
        closed_count = 0
        for _ in range(count):
            client, server = create_local_tcp_connection()
            client.close()
            server.close()
            closed_count += 1

        return ResourceDemoResult(
            resource_type="socket",
            opened_count=count,
            closed_count=closed_count,
            outstanding_count=0,
        )

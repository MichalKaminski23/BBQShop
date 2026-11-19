"""Szkielet wersji podatnej."""

from bbq_fdleak.schemas import ResourceDemoResult


class VulnerableResourceRepository:
    def open_file(self, count: int) -> ResourceDemoResult:
        raise NotImplementedError("Implementacja wariantu podatnego zostanie dodana później.")

    def open_socket(self, count: int) -> ResourceDemoResult:
        raise NotImplementedError("Implementacja wariantu podatnego zostanie dodana później.")

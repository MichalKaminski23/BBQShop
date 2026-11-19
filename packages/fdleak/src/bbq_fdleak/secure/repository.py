"""Szkielet wersji poprawionej."""

from bbq_fdleak.schemas import ResourceDemoResult


class SecureResourceRepository:
    def open_file(self, count: int) -> ResourceDemoResult:
        raise NotImplementedError("Implementacja wariantu poprawionego zostanie dodana później.")

    def open_socket(self, count: int) -> ResourceDemoResult:
        raise NotImplementedError("Implementacja wariantu poprawionego zostanie dodana później.")

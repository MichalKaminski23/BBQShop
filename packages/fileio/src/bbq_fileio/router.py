"""Endpointy modułu File I/O - implementacja zależy od wariantu z ``.env``."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from bbq_core.module import Variant
from bbq_fileio.repository import FileRepository
from bbq_fileio.schemas import FileContent, WriteRequest, WriteResult
from bbq_fileio.secure import SecureFileRepository
from bbq_fileio.storage import default_root, prepare
from bbq_fileio.vulnerable import VulnerableFileRepository

REPOSITORIES: dict[Variant, type[FileRepository]] = {
    Variant.VULNERABLE: VulnerableFileRepository,
    Variant.SECURE: SecureFileRepository,
}

NameQuery = Annotated[str, Query(description="Nazwa pliku")]


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    base = prepare(default_root())
    router = APIRouter(prefix="/files", tags=["fileio"])

    @router.get("")
    async def read_file(name: NameQuery) -> FileContent:
        """Odczytuje plik o podanej nazwie."""
        try:
            return repository_cls(base).read(name)
        except OSError as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie można odczytać pliku") from error

    @router.post("", status_code=status.HTTP_201_CREATED)
    async def write_file(name: NameQuery, body: WriteRequest) -> WriteResult:
        """Zapisuje treść do pliku o podanej nazwie."""
        try:
            return repository_cls(base).write(name, body.content)
        except OSError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nie można zapisać pliku") from error

    return router

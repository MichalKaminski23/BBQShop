"""Endpoint modułu path traversal - implementacja zależy od wariantu z ``.env``."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from bbq_core.module import Variant
from bbq_path_traversal.repository import FileRepository
from bbq_path_traversal.schemas import FileOut
from bbq_path_traversal.secure import SecureFileRepository
from bbq_path_traversal.vulnerable import VulnerableFileRepository

BASE_DIR = Path(__file__).resolve().parent / "public"

REPOSITORIES: dict[Variant, type[FileRepository]] = {
    Variant.VULNERABLE: VulnerableFileRepository,
    Variant.SECURE: SecureFileRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    router = APIRouter(prefix="/files", tags=["path-traversal"])

    @router.get("", response_model=FileOut)
    def read_file(
        path: Annotated[str, Query(min_length=1, description="Ścieżka pliku")],
    ) -> FileOut | FileResponse:
        """Zwraca treść pliku demonstracyjnego."""
        try:
            repository = repository_cls(BASE_DIR)
            file = repository.path(path)
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Niedozwolona ścieżka pliku") from exc
        except FileNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Plik nie istnieje") from exc
        if file.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
            if not file.is_file():
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Plik nie istnieje")
            return FileResponse(file)
        return FileOut(filename=path, content=file.read_text(encoding="utf-8"))

    return router

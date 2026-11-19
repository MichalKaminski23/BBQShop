"""Endpointy demonstracji deskryptorów plików i gniazd."""

from fastapi import APIRouter, Query

from bbq_core.module import Variant
from bbq_fdleak.repository import ResourceRepository
from bbq_fdleak.schemas import ResourceDemoResult
from bbq_fdleak.secure import SecureResourceRepository
from bbq_fdleak.vulnerable import VulnerableResourceRepository

REPOSITORIES: dict[Variant, type[ResourceRepository]] = {
    Variant.VULNERABLE: VulnerableResourceRepository,
    Variant.SECURE: SecureResourceRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    router = APIRouter(prefix="/fdleak", tags=["fdleak"])
    repository = repository_cls()

    @router.get("/file", response_model=ResourceDemoResult)
    def open_file(
        count: int = Query(default=1, ge=1, le=100),
    ) -> ResourceDemoResult:
        return repository.open_file(count)

    @router.get("/socket", response_model=ResourceDemoResult)
    def open_socket(
        count: int = Query(default=1, ge=1, le=100),
    ) -> ResourceDemoResult:
        return repository.open_socket(count)

    return router

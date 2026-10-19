"""Endpointy systemowe: stan baz danych i lista modułów."""

from typing import Literal, cast

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from bbq_api.registry import ActiveModule
from bbq_core.deps import MongoDep, SessionDep
from bbq_core.module import Variant

router = APIRouter(tags=["system"])

type ServiceStatus = Literal["ok", "error"]


class HealthResponse(BaseModel):
    postgres: ServiceStatus
    mongo: ServiceStatus


class ModuleInfo(BaseModel):
    name: str
    title: str
    description: str
    variant: Variant


@router.get("/health")
async def health(session: SessionDep, mongo: MongoDep, response: Response) -> HealthResponse:
    """Sprawdza połączenie z PostgreSQL i MongoDB."""
    result = HealthResponse(postgres="ok", mongo="ok")
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        result.postgres = "error"
    try:
        await mongo.command("ping")
    except Exception:
        result.mongo = "error"

    if "error" in (result.postgres, result.mongo):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result


@router.get("/modules")
async def list_modules(request: Request) -> list[ModuleInfo]:
    """Lista modułów podatności z aktywnym wariantem."""
    active = cast(list[ActiveModule], request.app.state.modules)
    return [
        ModuleInfo(
            name=item.module.name,
            title=item.module.title,
            description=item.module.description,
            variant=item.variant,
        )
        for item in active
    ]

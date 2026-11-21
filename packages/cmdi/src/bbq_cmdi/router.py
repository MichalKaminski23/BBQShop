from fastapi import APIRouter, HTTPException, Query

from bbq_cmdi.schemas import PingResult
from bbq_cmdi.secure.executor import SecurePingExecutor
from bbq_cmdi.vulnerable.executor import VulnerablePingExecutor
from bbq_core.module import Variant


def build_router(variant: Variant) -> APIRouter:
    router = APIRouter(prefix="/cmdi", tags=["cmdi"])
    executor = VulnerablePingExecutor() if variant == Variant.VULNERABLE else SecurePingExecutor()

    @router.get("/ping", response_model=PingResult)
    async def ping(
        host: str = Query(default="127.0.0.1", max_length=512),
    ) -> PingResult:
        if not host.strip():
            raise HTTPException(status_code=400, detail="Podaj host do diagnozowania.")
        return await executor.execute(host)

    return router

"""Command injection in a network diagnostic endpoint."""

from bbq_cmdi.router import build_router
from bbq_core.module import BBQModule

module = BBQModule(
    name="cmdi",
    title="Command Injection",
    description="Wstrzyknięcie polecenia w parametrze diagnostyki sieciowej.",
    build_router=build_router,
)

__all__ = ["module"]

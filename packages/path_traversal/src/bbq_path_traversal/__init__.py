"""Path traversal w endpointcie odczytu plików."""

from bbq_core.module import BBQModule
from bbq_path_traversal.router import build_router

module = BBQModule(
    name="path_traversal",
    title="Path Traversal",
    description="Endpoint odczytu plików podatny na wyjście poza katalog bazowy.",
    build_router=build_router,
)

__all__ = ["module"]

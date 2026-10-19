"""Odkrywanie modułów podatności przez entry points."""

from dataclasses import dataclass
from importlib.metadata import entry_points

from bbq_core.config import Settings
from bbq_core.module import ENTRY_POINT_GROUP, BBQModule, Variant


@dataclass(frozen=True, slots=True)
class ActiveModule:
    """Moduł razem z wariantem wybranym w konfiguracji."""

    module: BBQModule
    variant: Variant

    @property
    def enabled(self) -> bool:
        return self.variant is not Variant.OFF


def discover_modules() -> list[BBQModule]:
    """Ładuje wszystkie zainstalowane moduły z grupy ``bbqshop.modules``."""
    modules: list[BBQModule] = []
    for entry_point in entry_points(group=ENTRY_POINT_GROUP):
        obj = entry_point.load()
        if not isinstance(obj, BBQModule):
            msg = f"Entry point {entry_point.value!r} nie wskazuje na BBQModule"
            raise TypeError(msg)
        modules.append(obj)
    return sorted(modules, key=lambda m: m.name)


def resolve_modules(modules: list[BBQModule], settings: Settings) -> list[ActiveModule]:
    """Przypisuje każdemu modułowi wariant z konfiguracji."""
    return [ActiveModule(module, settings.variant_for(module.name)) for module in modules]

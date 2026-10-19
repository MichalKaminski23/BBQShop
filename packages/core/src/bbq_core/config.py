"""Konfiguracja aplikacji wczytywana ze zmiennych środowiskowych i pliku ``.env``."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bbq_core.module import Variant

ENV_PREFIX = "BBQ_"
MODULE_PREFIX = f"{ENV_PREFIX}MODULE_"


class ConfigError(ValueError):
    """Niepoprawna wartość w konfiguracji."""


class Settings(BaseSettings):
    """Ustawienia aplikacji (zmienne z prefiksem ``BBQ_``)."""

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, env_file=".env", extra="ignore")

    postgres_dsn: str = "postgresql+asyncpg://bbq:bbq@localhost:5432/bbqshop"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "bbqshop"
    default_variant: Variant = Variant.SECURE
    seed_on_startup: bool = True
    modules: dict[str, Variant] = Field(default_factory=dict)

    def variant_for(self, module_name: str) -> Variant:
        """Zwraca wariant modułu: własne ustawienie albo ``default_variant``."""
        return self.modules.get(module_name.lower(), self.default_variant)


def read_module_variants(env_file: Path | None = Path(".env")) -> dict[str, Variant]:
    """Zbiera zmienne ``BBQ_MODULE_<NAME>`` z pliku ``.env`` i środowiska.

    Zmienne środowiskowe mają pierwszeństwo przed plikiem ``.env``.

    Raises:
        ConfigError: Gdy wartość nie jest jednym z wariantów.
    """
    file_values = dotenv_values(env_file) if env_file is not None and env_file.exists() else {}
    merged = {**file_values, **os.environ}

    variants: dict[str, Variant] = {}
    for key, raw in merged.items():
        if not key.upper().startswith(MODULE_PREFIX) or raw is None:
            continue
        name = key[len(MODULE_PREFIX) :].lower()
        try:
            variants[name] = Variant(raw.strip().lower())
        except ValueError:
            allowed = ", ".join(v.value for v in Variant)
            msg = f"{key}={raw!r}: dozwolone wartości to {allowed}"
            raise ConfigError(msg) from None
    return variants


@lru_cache
def get_settings() -> Settings:
    """Zwraca (zapamiętane) ustawienia aplikacji."""
    return Settings(modules=read_module_variants())

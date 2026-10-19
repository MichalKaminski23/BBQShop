from pathlib import Path

import pytest

from bbq_core.config import ConfigError, Settings, read_module_variants
from bbq_core.module import Variant


def test_reads_module_variants_from_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("BBQ_MODULE_SQLI=vulnerable\nBBQ_MODULE_NOSQLI=OFF\nOTHER=1\n")

    assert read_module_variants(env_file) == {"sqli": Variant.VULNERABLE, "nosqli": Variant.OFF}


def test_environment_overrides_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("BBQ_MODULE_SQLI=vulnerable\n")
    monkeypatch.setenv("BBQ_MODULE_SQLI", "secure")

    assert read_module_variants(env_file)["sqli"] is Variant.SECURE


def test_invalid_variant_gives_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BBQ_MODULE_SQLI", "maybe")

    with pytest.raises(ConfigError, match="BBQ_MODULE_SQLI"):
        read_module_variants(None)


def test_variant_for_falls_back_to_default() -> None:
    settings = Settings(default_variant=Variant.SECURE, modules={"sqli": Variant.VULNERABLE})

    assert settings.variant_for("SQLI") is Variant.VULNERABLE
    assert settings.variant_for("race") is Variant.SECURE

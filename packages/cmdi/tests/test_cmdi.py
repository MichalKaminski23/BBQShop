"""Testy walidacji i wariantów modułu Command Injection."""

import pytest
from fastapi import HTTPException

from bbq_cmdi.secure.executor import SecurePingExecutor, validate_host


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "bbqshop.local", "192.168.1.10"])
def test_secure_accepts_normal_hosts(host: str) -> None:
    assert validate_host(host) == host


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1; echo injected", "$(whoami)", "../etc/passwd", "host/name"],
)
def test_secure_rejects_shell_metacharacters(host: str) -> None:
    with pytest.raises(HTTPException) as exc:
        validate_host(host)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_secure_uses_no_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []

    class Process:
        returncode = 0

        async def communicate(self) -> tuple[bytes, None]:
            return b"ok", None

    async def fake_exec(*args: str, **kwargs: object) -> Process:
        captured.extend(args)
        return Process()

    monkeypatch.setattr("bbq_cmdi.secure.executor.asyncio.create_subprocess_exec", fake_exec)
    result = await SecurePingExecutor().execute("127.0.0.1")

    assert captured[:2] == ["ping", "-n"] or captured[:2] == ["ping", "-c"]
    assert captured[-1] == "127.0.0.1"
    assert result.output == "ok"

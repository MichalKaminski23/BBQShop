import asyncio
import ipaddress
import platform
import re

from fastapi import HTTPException, status

from bbq_cmdi.schemas import PingResult


def validate_host(host: str) -> str:
    value = host.strip()
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError:
        pass
    labels = value.rstrip(".").split(".")
    if len(value.rstrip(".")) <= 253 and all(
        label
        and len(label) <= 63
        and re.fullmatch(r"[A-Za-z0-9-]+", label)
        and not label.startswith("-")
        and not label.endswith("-")
        for label in labels
    ):
        return value
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Podaj poprawny adres IP lub nazwę hosta.",
    )


class SecurePingExecutor:
    async def execute(self, host: str) -> PingResult:
        host = validate_host(host)
        count_option = "-n" if platform.system() == "Windows" else "-c"
        command_args = ["ping", count_option, "2", host]
        process = await asyncio.create_subprocess_exec(
            *command_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await process.communicate()
        command = " ".join(command_args)
        return PingResult(
            host=host,
            command=command,
            exit_code=process.returncode,
            output=stdout.decode("utf-8", errors="replace").strip(),
        )

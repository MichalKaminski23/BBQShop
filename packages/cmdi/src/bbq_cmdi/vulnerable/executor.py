import asyncio
import platform

from bbq_cmdi.schemas import PingResult


class VulnerablePingExecutor:
    async def execute(self, host: str) -> PingResult:
        count_option = "-n" if platform.system() == "Windows" else "-c"
        count = "2"
        command = f"ping {count_option} {count} {host}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await process.communicate()
        return PingResult(
            host=host,
            command=command,
            exit_code=process.returncode,
            output=stdout.decode("utf-8", errors="replace").strip(),
        )

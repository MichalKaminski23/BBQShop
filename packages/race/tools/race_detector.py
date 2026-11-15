#!/usr/bin/env python3
"""HTTP detector for the one-use GRILL10 coupon race condition."""

import argparse
import asyncio
import json
import os
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@dataclass
class SeriesResult:
    series: int
    status_counts: dict[str, int]
    accepted: int
    connection_errors: int
    server_errors: int
    other_errors: int
    valid: bool


def app_dsn() -> str:
    env_file = Path(".env")
    file_value: str | None = None
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() == "BBQ_POSTGRES_DSN":
                file_value = value.strip().strip("\"'")
                break
    return os.environ.get(
        "BBQ_POSTGRES_DSN",
        file_value or "postgresql+asyncpg://bbq:bbq@localhost:5432/bbqshop",
    )


async def reset_coupon(dsn: str) -> None:
    """Reset only the named demo coupon; fail if it is missing."""
    engine = create_async_engine(dsn, pool_pre_ping=True)
    try:
        async with engine.begin() as connection:
            result = await connection.execute(
                text("UPDATE coupons SET uses_left = 1 WHERE code = :code"),
                {"code": "GRILL10"},
            )
            if result.rowcount != 1:
                raise RuntimeError("Reset GRILL10 expected exactly one row")
    finally:
        await engine.dispose()


async def run_series(
    client: httpx.AsyncClient, endpoint: str, count: int, request_timeout: float, series: int
) -> SeriesResult:
    ready = 0
    start = asyncio.Event()
    lock = asyncio.Lock()

    async def redeem() -> tuple[int | None, str | None]:
        nonlocal ready
        async with lock:
            ready += 1
            if ready == count:
                start.set()
        await start.wait()
        try:
            response = await client.post(
                endpoint, json={"code": "GRILL10"}, timeout=request_timeout
            )
            return response.status_code, None
        except httpx.TimeoutException:
            return None, "timeout"
        except httpx.RequestError:
            return None, "connection"

    responses = await asyncio.gather(*(redeem() for _ in range(count)))
    counts = Counter(str(status) for status, _ in responses if status is not None)
    accepted = counts.get("200", 0)
    connection_errors = sum(error == "connection" for _, error in responses)
    other_errors = sum(error == "timeout" for _, error in responses)
    server_errors = sum(count for code, count in counts.items() if int(code) >= 500)
    valid = (
        connection_errors == 0
        and other_errors == 0
        and server_errors == 0
        and counts.get("404", 0) == 0
        and counts.get("409", 0) == count - accepted
        and accepted >= 1
    )
    return SeriesResult(
        series=series,
        status_counts=dict(counts),
        accepted=accepted,
        connection_errors=connection_errors,
        server_errors=server_errors,
        other_errors=other_errors,
        valid=valid,
    )


async def detect(args: argparse.Namespace) -> dict[str, Any]:
    base = args.url.rstrip("/")
    results: list[SeriesResult] = []
    async with httpx.AsyncClient(base_url=base) as client:
        for number in range(1, args.repeats + 1):
            try:
                await reset_coupon(args.postgres_dsn)
            except Exception as exc:
                return {
                    "result": "INCONCLUSIVE",
                    "reason": f"coupon reset failed: {exc}",
                    "series": [],
                }
            result = await run_series(
                client,
                f"{base}/api/race/coupons/redeem",
                args.requests,
                args.timeout,
                number,
            )
            results.append(result)

    if any(not result.valid for result in results):
        verdict = "INCONCLUSIVE"
    elif any(result.accepted > 1 for result in results):
        verdict = "VULNERABLE"
    else:
        verdict = "NO_RACE_OBSERVED"
    return {"result": verdict, "series": [asdict(result) for result in results]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--requests", type=int, default=20, help="Concurrent requests per series")
    parser.add_argument(
        "--repeats", type=int, default=5, help="Number of independently reset series"
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--postgres-dsn", default=None, help="Override app PostgreSQL DSN")
    parser.add_argument("--json", dest="json_path", help="Write full report to this JSON file")
    args = parser.parse_args()
    args.postgres_dsn = args.postgres_dsn or app_dsn()
    if args.requests < 2 or args.repeats < 1 or args.timeout <= 0:
        parser.error("requests must be >=2, repeats >=1, timeout >0")
    report = asyncio.run(detect(args))
    print(f"Wynik: {report['result']}")
    for result in report["series"]:
        print(
            f"Seria {result['series']}: accepted={result['accepted']}, "
            f"HTTP={result['status_counts']}, valid={result['valid']}"
        )
    if report.get("reason"):
        print(f"Powód: {report['reason']}")
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    raise SystemExit({"VULNERABLE": 1, "NO_RACE_OBSERVED": 0, "INCONCLUSIVE": 2}[report["result"]])


if __name__ == "__main__":
    main()

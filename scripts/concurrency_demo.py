"""Demonstracja wielokrotnego wykonania operacji skladania zamowienia."""

from __future__ import annotations

import argparse
import http.client
import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "scripts" / "reports"
SQL_MARKERS = ("SELECT", "INSERT", "UPDATE", "DELETE", "BEGIN", "COMMIT", "ROLLBACK")


def capture_api_logs() -> str:
    docker = shutil.which("docker")
    if docker is None:
        return ""

    completed = subprocess.run(  # noqa: S603
        [docker, "compose", "logs", "--tail=500", "api"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout + completed.stderr


def find_new_sql_lines(before: str, after: str) -> list[str]:
    before_lines = set(before.splitlines())
    return [
        line
        for line in after.splitlines()
        if line not in before_lines and any(marker in line.upper() for marker in SQL_MARKERS)
    ]


def get_json(base_url: str, path: str) -> tuple[object, object]:
    url = f"{base_url}{path}"
    if urlparse(url).scheme not in {"http", "https"}:
        raise RuntimeError("Dozwolony jest tylko HTTP lub HTTPS")

    request = urllib.request.Request(url, method="GET")  # noqa: S310
    with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310
        body = json.loads(response.read().decode("utf-8"))
        return body, response.headers


def wait_for_api(base_url: str) -> None:
    for _ in range(30):
        try:
            get_json(base_url, "/api/health")
            return
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            http.client.RemoteDisconnected,
            ConnectionResetError,
            ConnectionAbortedError,
        ):
            time.sleep(0.5)
    raise RuntimeError(f"API nie odpowiada pod {base_url}")


def post_order(
    base_url: str,
    payload: dict[str, object],
    idempotency_key: str,
) -> dict[str, object]:
    url = f"{base_url}/api/orders"
    if urlparse(url).scheme not in {"http", "https"}:
        raise RuntimeError("Dozwolony jest tylko HTTP lub HTTPS")

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        status = error.code
        body = json.loads(error.read().decode("utf-8"))

    if not isinstance(body, dict):
        raise RuntimeError(f"Niepoprawna odpowiedź POST /api/orders: {body!r}")
    body["http_status"] = status
    return body


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wysyla 8 równoległych żądań do wariantu concurrency."
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Bazowy adres API.",
    )
    parser.add_argument(
        "--customer-name",
        default="Concurrency demo",
        help="Nazwa klienta w tworzonych zamówieniach.",
    )
    parser.add_argument(
        "--product-id",
        type=int,
        default=1,
        help="ID produktu zamówienia.",
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=1,
        help="Ilość produktu.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=8,
        choices=range(2, 21),
        help="Liczba równoległych żądań (2-20).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    wait_for_api(args.base_url)

    modules, _ = get_json(args.base_url, "/api/modules")
    if not isinstance(modules, list):
        raise RuntimeError("Niepoprawna odpowiedź /api/modules")

    active = next(
        (
            module
            for module in modules
            if isinstance(module, dict) and module.get("name") == "concurrency"
        ),
        None,
    )
    actual_variant = active.get("variant") if active is not None else None
    if actual_variant not in {"vulnerable", "secure"}:
        raise RuntimeError(f"Nie można odczytać aktywnego wariantu concurrency: {actual_variant!r}")
    variant = str(actual_variant)

    payload: dict[str, object] = {
        "customer_name": args.customer_name,
        "items": [{"product_id": args.product_id, "quantity": args.quantity}],
    }
    idempotency_key = str(uuid.uuid4())

    logs_before = capture_api_logs()
    responses: list[dict[str, object]] = []
    started = time.monotonic()

    with ThreadPoolExecutor(max_workers=args.count) as executor:
        futures = [
            executor.submit(post_order, args.base_url, payload, idempotency_key)
            for _ in range(args.count)
        ]
        for future in as_completed(futures):
            responses.append(future.result())

    elapsed_ms = (time.monotonic() - started) * 1000
    logs_after = capture_api_logs()
    sql_lines = find_new_sql_lines(logs_before, logs_after)

    order_ids: set[int] = set()
    created_flags: list[bool] = []
    statuses: list[int] = []
    for response in responses:
        statuses.append(int(response["http_status"]))
        created = response.get("created")
        if isinstance(created, bool):
            created_flags.append(created)
        order = response.get("order")
        if isinstance(order, dict) and isinstance(order.get("id"), int):
            order_ids.add(order["id"])

    expected_unique = args.count if variant == "vulnerable" else 1
    unique_count = len(order_ids)
    if unique_count != expected_unique:
        raise RuntimeError(
            f"Wariant {variant}: otrzymano {unique_count} unikalnych zamówień, "
            f"oczekiwano {expected_unique}"
        )

    print(f"\nDemonstracja współbieżności - wariant {variant}")
    print(f"Liczba równoległych żądań: {args.count}")
    print(f"Idempotency-Key: {idempotency_key}")
    print(f"Klient: {args.customer_name}")
    print(f"Produkt #{args.product_id}, ilość: {args.quantity}")
    print(f"Unikalne zamówienia: {unique_count}")
    print(f"Czas całej demonstracji: {elapsed_ms:.2f} ms")
    print(
        f"Kody HTTP: {dict(sorted((status, statuses.count(status)) for status in set(statuses)))}"
    )
    print(f"Wartości created: {created_flags.count(True)} true, {created_flags.count(False)} false")
    print(f"ID zamówień: {', '.join(str(order_id) for order_id in sorted(order_ids))}")

    if variant == "vulnerable":
        print("Wynik: Wielokrotne wykonanie wykryte")
        print("Działanie: każdy równoległy request utworzył osobne zamówienie")
    else:
        print("Wynik: Wielokrotne wykonanie ograniczone")
        print("Działanie: jeden klucz idempotencji zwrócił jedno zamówienie")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"concurrency-{variant}-{timestamp}.txt"

    report_lines = [
        "Demonstracja wielokrotnego wykonania operacji",
        f"Czas: {datetime.now().isoformat(timespec='seconds')}",
        f"Wariant: {variant}",
        f"Liczba równoległych żądań: {args.count}",
        f"Idempotency-Key: {idempotency_key}",
        f"Klient: {args.customer_name}",
        f"Produkt #{args.product_id}, ilość: {args.quantity}",
        f"Unikalne zamówienia: {unique_count}",
        f"Oczekiwana liczba unikalnych zamówień: {expected_unique}",
        f"Czas całej demonstracji: {elapsed_ms:.2f} ms",
        f"Kody HTTP: {dict(sorted((status, statuses.count(status)) for status in set(statuses)))}",
        f"Wartości created: {created_flags.count(True)} true, {created_flags.count(False)} false",
        f"ID zamówień: {', '.join(str(order_id) for order_id in sorted(order_ids))}",
        "",
        "Logi SQL z wykonania:",
    ]
    if sql_lines:
        report_lines.extend(sql_lines)
    else:
        report_lines.append(
            "(Nie znaleziono nowych linii SQL. Sprawdź BBQ_DB_METRICS=true "
            "i konfigurację logowania SQL)"
        )

    report_path.write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8")
    print(f"\nRaport zapisano: {report_path}")


if __name__ == "__main__":
    main()

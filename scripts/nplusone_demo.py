"""Demonstracja problemu N+1 dla aktualnie aktywnego wariantu."""

from __future__ import annotations

import argparse
import http.client
import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pokazuje liczbę zapytań SQL dla aktualnego wariantu N+1.")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Bazowy adres API.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        choices=range(1, 21),
        help="Liczba zamówień pokazanych na ekranie (1-20).",
    )
    parser.add_argument(
        "--customer-name",
        help="Filtruje zamówienia po nazwie klienta, np. 'Jan Kowalski'.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    wait_for_api(args.base_url)

    modules, _ = get_json(args.base_url, "/api/modules")
    if not isinstance(modules, list):
        raise RuntimeError("Niepoprawna odpowiedź /api/modules")

    active = next(
        (module for module in modules if isinstance(module, dict) and module.get("name") == "nplusone"),
        None,
    )
    actual_variant = active.get("variant") if active is not None else None
    if actual_variant not in {"vulnerable", "secure"}:
        raise RuntimeError(f"Nie można odczytać aktywnego wariantu N+1: {actual_variant!r}")
    variant = str(actual_variant)

    logs_before = capture_api_logs()
    orders_path = "/api/orders"
    if args.customer_name:
        orders_path = f"{orders_path}?{urlencode({'customer_name': args.customer_name})}"

    body, headers = get_json(args.base_url, orders_path)
    logs_after = capture_api_logs()
    sql_lines = find_new_sql_lines(logs_before, logs_after)
    if not isinstance(body, list):
        raise RuntimeError("Endpoint /api/orders nie zwrócił listy")

    query_count_header = headers.get("X-SQL-Query-Count")
    query_time_header = headers.get("X-SQL-Query-Time-Ms")
    if query_count_header is None or query_time_header is None:
        raise RuntimeError("Brakuje nagłówków SQL. Ustaw BBQ_DB_METRICS=true i przeładuj API.")

    query_count = int(query_count_header)
    query_time = float(query_time_header)
    order_count = len(body)
    expected = order_count + 1 if variant == "vulnerable" else 2

    print(f"\nDemonstracja N+1 - wariant {variant}")
    if args.customer_name:
        print(f"Klient: {args.customer_name}")
    print(f"Liczba zamówień: {order_count}")
    print(f"Liczba zapytań SQL: {query_count}")
    print(f"Oczekiwana liczba: {expected}")
    print(f"Czas zapytań SQL: {query_time:.2f} ms")

    if query_count != expected:
        raise RuntimeError(f"Otrzymano {query_count} zapytań, oczekiwano {expected}")

    print(f"\nPierwsze zamówienia (limit: {args.limit}):")
    for order in body[: args.limit]:
        if not isinstance(order, dict):
            continue

        print(f"- #{order.get('id')} | " f"{order.get('customer_name')} | " f"utworzono: {order.get('created_at')}")
        items = order.get("items")
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            print(
                f"  - produkt #{item.get('product_id')}, "
                f"ilość: {item.get('quantity')}, "
                f"cena: {item.get('unit_price')}"
            )

    if variant == "vulnerable":
        print("Wynik: PODATNOŚĆ WYKRYTA")
        print("Działanie: 1 zapytanie o zamówienia + osobne zapytanie dla każdego zamówienia")
    else:
        print("Wynik: PODATNOŚĆ NIEOBECNA")
        print("Działanie: selectinload pobiera pozycje w jednym dodatkowym zapytaniu")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"nplusone-{variant}-{timestamp}.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "Demonstracja problemu N+1",
        f"Czas: {datetime.now().isoformat(timespec='seconds')}",
        f"Wariant: {variant}",
        f"Klient: {args.customer_name or 'wszyscy'}",
        f"Liczba zamówień: {order_count}",
        f"Liczba zapytań SQL: {query_count}",
        f"Oczekiwana liczba: {expected}",
        f"Czas zapytań SQL: {query_time:.2f} ms",
        "",
        "Logi SQL z wykonania:",
    ]
    if sql_lines:
        report_lines.extend(sql_lines)
    else:
        report_lines.append(
            "(Nie znaleziono nowych linii SQL. Sprawdź, czy BBQ_DB_METRICS=true "
            "i czy echo SQL jest włączone w konfiguracji Docker)"
        )

    report_lines.extend(["", "Zamówienia i pozycje:"])
    for order in body[: args.limit]:
        if not isinstance(order, dict):
            continue
        report_lines.append(
            f"- #{order.get('id')} | {order.get('customer_name')} " f"| utworzono: {order.get('created_at')}"
        )
        items = order.get("items")
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            report_lines.append(
                f"  - produkt #{item.get('product_id')}, "
                f"ilość: {item.get('quantity')}, cena: {item.get('unit_price')}"
            )

    report_path.write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8")
    print(f"\nRaport zapisano: {report_path}")


if __name__ == "__main__":
    main()

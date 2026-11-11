# Uruchomienie i codzienna praca

Ta strona zawiera wspólne komendy dla całego projektu. Instrukcje
demonstracji konkretnych podatności znajdują się w
[indeksie dokumentacji](README.md).

> Projekt jest celowo podatny i służy wyłącznie do nauki. Uruchamiaj go
> lokalnie i nie wystawiaj publicznie do internetu.

## Wymagania

- Docker z Docker Compose,
- `uv`,
- Node 24 (tylko przy lokalnym uruchamianiu frontendu),
- Git.

Sprawdzenie instalacji:

```powershell
docker --version
docker compose version
uv --version
node --version
```

## Konfiguracja

Utwórz lokalny plik konfiguracyjny:

```powershell
Copy-Item .env.example .env
```

W `.env` wybierasz wariant każdego modułu:

```dotenv
BBQ_DEFAULT_VARIANT=secure
BBQ_MODULE_SQLI=vulnerable
BBQ_MODULE_NOSQLI=vulnerable
BBQ_MODULE_NPLUSONE=vulnerable
BBQ_MODULE_CONCURRENCY=secure
```

Dostępne wartości to `vulnerable`, `secure` i `off`.
`BBQ_DB_METRICS=true` włącza demonstracyjne nagłówki i logowanie zapytań
SQL dla zakładki Zamówienia. Domyślnie pozostaw tę opcję wyłączoną.

## Uruchomienie w Dockerze

Z głównego katalogu repozytorium:

```powershell
docker compose up --build -d
```

Adresy:

| Usługa | Adres |
|---|---|
| Frontend | http://localhost:5173 |
| Sklep | http://localhost:5173/shop |
| Zamówienia | http://localhost:5173/orders |
| Współbieżność | http://localhost:5173/concurrency |
| Logowanie | http://localhost:5173/login |
| Swagger | http://localhost:8000/docs |
| Stan usług | http://localhost:8000/api/health |
| Aktywne moduły | http://localhost:8000/api/modules |

Przebuduj tylko API po zmianie backendu:

```powershell
docker compose up --build -d api
```

Po zmianie samego `.env` odtwórz kontener API:

```powershell
docker compose up -d --force-recreate api
```

Po zmianie frontendu Vite zwykle odświeży stronę automatycznie. W razie
problemu:

```powershell
docker compose restart frontend
```

## Zatrzymywanie i logi

Zatrzymanie kontenerów z zachowaniem danych:

```powershell
docker compose down
```

Zatrzymanie bez usuwania kontenerów:

```powershell
docker compose stop
```

Ponowne uruchomienie:

```powershell
docker compose start
```

Status:

```powershell
docker compose ps
```

Logi API:

```powershell
docker compose logs -f --tail=100 api
```

## Świeże dane testowe

Seed uruchamia się tylko dla pustych tabel i kolekcji. Aby usunąć lokalne
wolumeny i odtworzyć bazę od początku:

```powershell
docker compose down -v
docker compose up --build -d
```

> `down -v` usuwa lokalne dane PostgreSQL i MongoDB.

## Tryb deweloperski

W tym trybie bazy działają w Dockerze, a API i frontend lokalnie.

Terminal 1 — bazy:

```powershell
docker compose up -d postgres mongo
```

Terminal 2 — backend:

```powershell
uv sync
uv run alembic -c packages/db/alembic.ini upgrade head
uv run bbq-api
```

Terminal 3 — frontend:

```powershell
Set-Location frontend
npm ci
npm run dev
```

API działa pod http://localhost:8000, a frontend pod
http://localhost:5173. API i frontend zatrzymasz przez `Ctrl+C`.

## Przełączanie wariantu modułu

1. Zmień `BBQ_MODULE_<NAZWA>` w `.env`.
2. W Dockerze wykonaj:

   ```powershell
   docker compose up -d --force-recreate api
   ```

3. W trybie lokalnym zatrzymaj `bbq-api` i uruchom je ponownie:

   ```powershell
   uv run bbq-api
   ```

Aktywny wariant sprawdzisz na stronie głównej albo przez:

```text
http://localhost:8000/api/modules
```

## Testy i jakość

Wszystkie testy:

```powershell
uv run pytest
```

Tylko testy bez Dockera:

```powershell
uv run pytest -m "not integration"
```

Backend:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Frontend:

```powershell
Set-Location frontend
npm run lint
npm run typecheck
npm run build
```

Hooki Git:

```powershell
uv run pre-commit install
uv run pre-commit run --all-files
```

## Demonstracje

Szczegółowe scenariusze są utrzymywane osobno:

- [SQL Injection](podatnosci/SQLi.md)
- [NoSQL Injection](podatnosci/NoSQLi.md)
- [Problem N+1](podatnosci/Nplusone.md)
- [Współbieżność i idempotencja](podatnosci/Concurrency.md)

## Najczęstsze problemy

- **Port zajęty** — sprawdź proces używający portu albo wykonaj
  `docker compose down`.
- **Frontend nie widzi zmian w Dockerze** — wykonaj
  `docker compose restart frontend` i odśwież stronę przez
  `Ctrl+Shift+R`.
- **Brak nowych danych seed** — seed działa tylko dla pustych baz; użyj
  `docker compose down -v`, jeśli potrzebujesz świeżego stanu.
- **Zmiana backendu nie jest widoczna** — przebuduj API przez
  `docker compose up --build -d api`.

# BBQShop

Aplikacja webowa imitująca sklep z produktami na grilla. W aplikacji **celowo umieszczono podatności**. Każda z nich ma też **poprawioną (bezpieczną) wersję kodu**, żeby obie wersje dało się porównać i przetestować.

> ⚠️ **Uwaga:** projekt jest celowo podatny i służy wyłącznie do celów edukacyjnych (przedmiot TBO). Nie uruchamiaj go w środowisku produkcyjnym ani nie wystawiaj publicznie do internetu.

## Skład sekcji

- Michał Kamiński
- Błażej Sztefka
- Jakub Gnela
- Patryk Czakon
- Wojciech Kierat
- Radosław Rajda

## Technologie

| Warstwa      | Technologia            |
|--------------|------------------------|
| Backend      | Python (FastAPI)       |
| Frontend     | React                  |
| Bazy danych  | PostgreSQL, MongoDB    |

## Podatności

Każda podatność występuje w dwóch wariantach: **podatnym** i **poprawionym**.

| # | Podatność                                                     |
|---|---------------------------------------------------------------|
| 1 | SQL Injection (SQLi)                                          |
| 2 | NoSQL Injection (NoSQLi)                                      |
| 3 | Command Injection                                             |
| 4 | Path Traversal                                                |
| 5 | Arbitrary File Read / Write                                   |
| 6 | Race Conditions                                               |
| 7 | Problem N+1                                                   |
| 8 | Nieograniczona współbieżność / wielokrotne wykonanie operacji |
| 9 | Niepoprawne zarządzanie deskryptorami plików i gniazd         |

## Architektura

Zgodnie z uwagami z 19.10:

- Projekt jest podzielony na **osobne paczki (moduły Pythonowe)** w [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/), po jednej na każdą podatność.
- **FastAPI** pełni rolę warstwy łączącej moduły i wystawia ich funkcje przez API dla frontendu w React.
- Każdy moduł ma **testy automatyczne**, które sprawdzają zarówno wersję podatną, jak i poprawioną.

```
packages/
├─ core/   bbq_core   # konfiguracja, połączenia z bazami, kontrakt modułu
├─ db/     bbq_db     # wspólna baza: modele, kolekcje Mongo, migracje, dane przykładowe
├─ api/    bbq_api    # aplikacja FastAPI, rejestr modułów, endpointy systemowe
└─ sqli/   bbq_sqli   # moduł podatności (wzór dla kolejnych)
frontend/             # React + Vite + TypeScript
```

### Baza danych (`packages/db`)

Schemat jest wspólny i minimalny: zawiera tylko to, czego potrzebują demonstracje podatności. Moduły z niego korzystają i nie definiują własnych tabel.

| Gdzie      | Tabela / kolekcja | Do czego                                                 |
|------------|-------------------|----------------------------------------------------------|
| PostgreSQL | `products`        | wyszukiwarka (SQLi), stan magazynu (race condition)      |
| PostgreSQL | `admin_secrets`   | fikcyjne sekrety, cel ataku SQLi                         |
| PostgreSQL | `orders`          | lista zamówień (N+1), wielokrotne złożenie zamówienia    |
| PostgreSQL | `order_items`     | pozycje zamówień (N+1)                                   |
| PostgreSQL | `coupons`         | kupon jednorazowy (race condition)                       |
| MongoDB    | `users`           | logowanie (NoSQLi)                                       |

```
bbq_db/
├─ base.py        # klasa bazowa modeli
├─ models/        # tabele PostgreSQL
├─ mongo/         # kolekcje MongoDB
├─ migrations/    # migracje Alembic
├─ seed/          # dane przykładowe (data.py) i ich wstawianie (seed.py)
└─ testing.py     # fixtures pytest z bazami w Dockerze
```

Dane przykładowe są wstawiane przy starcie API, tylko do pustych tabel. Wszystkie hasła i sekrety w nich są fikcyjne.

### Moduł podatności

Każdy moduł ma ten sam układ, z wersją podatną i poprawioną w osobnych folderach:

```
bbq_<nazwa>/
├─ __init__.py       # rejestracja modułu (nazwa, tytuł, opis)
├─ router.py         # endpointy FastAPI, wybierają wersję wg .env
├─ schemas.py        # modele odpowiedzi API
├─ repository.py     # wspólny interfejs obu wersji
├─ vulnerable/       # ❌ wersja podatna
└─ secure/           # ✅ wersja poprawiona
README.md            # opis podatności, przykładowy atak, opis poprawki
tests/               # te same scenariusze uruchamiane na obu wersjach
```

### Wybór wariantu (`.env`)

Każdy moduł włączasz w wersji podatnej, poprawionej albo wyłączasz:

```
BBQ_DEFAULT_VARIANT=secure     # dla modułów bez własnego ustawienia
BBQ_MODULE_SQLI=vulnerable     # vulnerable | secure | off
```

Endpoint `GET /api/modules` zwraca aktywne warianty, a frontend pokazuje je na stronie głównej. Pełna lista zmiennych jest w [.env.example](.env.example).

## Jak uruchomić

Wymagania: [uv](https://docs.astral.sh/uv/), Docker, Node 24.

```bash
cp .env.example .env
```

**Wszystko w Dockerze:**

```bash
docker compose up --build
```

Frontend: http://localhost:5173, API: http://localhost:8000/docs.

**Tryb deweloperski** (bazy w Dockerze, reszta lokalnie):

```bash
docker compose up -d postgres mongo
```

```bash
uv sync
```

```bash
uv run alembic -c packages/db/alembic.ini upgrade head
```

```bash
uv run bbq-api
```

```bash
cd frontend && npm install && npm run dev
```

## Testy i jakość kodu

```bash
uv run pytest
```

Testy integracyjne (`-m integration`) startują Postgresa i MongoDB w Dockerze przez [testcontainers](https://testcontainers.com/). Bez Dockera uruchomisz same testy jednostkowe: `uv run pytest -m "not integration"`.

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy
```

Hooki przed commitem: `uv run pre-commit install`. CI (GitHub Actions) uruchamia to samo dla backendu oraz lint i build frontendu.

## Jak dodać nowy moduł

1. Skopiuj `packages/sqli` jako `packages/<nazwa>` i zmień nazwy (`bbq_<nazwa>`). Kod podatny trafia do `vulnerable/`, poprawiony do `secure/`.
2. W `packages/<nazwa>/pyproject.toml` zarejestruj moduł:
   ```toml
   [project.entry-points."bbqshop.modules"]
   <nazwa> = "bbq_<nazwa>:module"
   ```
3. Dodaj paczkę do `dependencies` i `[tool.uv.sources]` w głównym `pyproject.toml` oraz do `packages` w `[tool.mypy]`, potem `uv sync`.
4. Moduł korzysta ze wspólnego schematu z `bbq_db`. Gdyby naprawdę potrzebował nowej kolumny lub tabeli, dodaj model w `packages/db/src/bbq_db/models/` i migrację: `uv run alembic -c packages/db/alembic.ini revision --autogenerate -m "<opis>"`.
5. Dodaj `COPY packages/<nazwa>/pyproject.toml` w [packages/api/Dockerfile](packages/api/Dockerfile).
6. Ustaw `BBQ_MODULE_<NAZWA>` w `.env.example`.

API odkrywa moduł automatycznie. Nie trzeba zmieniać kodu `bbq_api`.

## Repozytorium

https://github.com/MichalKaminski23/BBQShop

## Harmonogram

| Data  | Wydarzenie                                                          |
|-------|---------------------------------------------------------------------|
| 19.10 | Uwagi do projektu: podział na moduły, testy, FastAPI jako warstwa łącząca |
| 02.11 | Spotkanie (zdalnie)                                                 |

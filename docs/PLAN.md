# Plan i status modułów

## Status modułów

| # | Moduł | Pakiet | Endpoint | Status | Osoba |
|---|---|---|---|---|---|
| 1 | SQL Injection | `bbq_sqli` | `GET /api/products/search` | ✅ gotowe | Błażej |
| 2 | NoSQL Injection | `bbq_nosqli` | `POST /api/login` | ✅ gotowe | Błażej |
| 3 | Command Injection | `bbq_cmdi` | `GET /api/cmdi/ping` | ✅ gotowe | Kuba |
| 4 | Path Traversal | `bbq_path_traversal` | `GET /api/files` | ✅ gotowe | Kuba |
| 5 | Arbitrary File Read / Write | `bbq_fileio` | `GET/POST /api/storage` | ✅ gotowe | Wojtek |
| 6 | Race Conditions | `bbq_race` | `GET/POST /api/race/coupons` | ✅ gotowe | Radek |
| 7 | Problem N+1 | `bbq_nplusone` | `GET /api/orders` | ✅ gotowe | Michał |
| 8 | Wielokrotne wykonanie / współbieżność | `bbq_concurrency` | `POST /api/orders` | ✅ gotowe | Michał |
| 9 | Deskryptory plików i gniazd | `bbq_fdleak` | `GET /api/fdleak/{file,socket}` | ✅ gotowe | Patryk |

Legenda: ✅ gotowe · 🟡 w trakcie · ⬜ do zrobienia

Dokumentacja demonstracji modułów:

- [SQL Injection](podatnosci/SQLi.md)
- [NoSQL Injection](podatnosci/NoSQLi.md)
- Command Injection — *dokument do uzupełnienia*
- Path Traversal — *dokument do uzupełnienia*
- [Arbitrary File Read / Write](podatnosci/FileIO.md)
- [Race Conditions](podatnosci/RaceConditions.md)
- [Problem N+1](podatnosci/Nplusone.md)
- [Współbieżność](podatnosci/Concurrency.md)
- [Deskryptory plików i gniazd](podatnosci/FdLeak.md)

## Standard nowego modułu

Każdy moduł powinien mieć:

```text
packages/<nazwa>/
├─ pyproject.toml
├─ README.md
├─ src/bbq_<nazwa>/
│  ├─ __init__.py
│  ├─ py.typed
│  ├─ repository.py
│  ├─ router.py
│  ├─ schemas.py
│  ├─ vulnerable/
│  └─ secure/
└─ tests/
```

Wariant `vulnerable` pokazuje problem edukacyjny, a `secure` poprawkę.
Oba warianty powinny zachować ten sam kontrakt endpointu.

## Checklista implementacji

- [ ] paczka i entry point `bbqshop.modules`,
- [ ] zależność w głównym `pyproject.toml` i `uv.lock`,
- [ ] wpis w `packages/api/Dockerfile`,
- [ ] ustawienie `BBQ_MODULE_<NAZWA>` w `.env.example`,
- [ ] modele/migracja, jeśli moduł wymaga zmian w bazie,
- [ ] wariant podatny i poprawiony,
- [ ] testy jednostkowe i integracyjne,
- [ ] dokumentacja w `packages/<nazwa>/README.md`,
- [ ] instrukcja demonstracji w `docs/podatnosci/<Nazwa>.md`,
- [ ] odnośnik w `docs/README.md`,
- [ ] przejście jakości:

  ```powershell
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy
  uv run pytest
  ```

API odkrywa moduły przez entry points. Nie należy dodawać ich ręcznie do
`bbq_api`.

## Status: wszystkie moduły gotowe

Wszystkie 9 modułów jest zaimplementowanych (wariant podatny i poprawiony),
zarejestrowanych przez entry points i dostępnych w API. Nie ma modułów
pozostających do zrobienia.

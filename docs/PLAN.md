# Plan i status modułów

## Status modułów

| # | Moduł | Pakiet | Endpoint | Status | Osoba |
|---|---|---|---|---|---|
| 1 | SQL Injection | `bbq_sqli` | `GET /api/products/search` | ✅ gotowe | Błażej |
| 2 | NoSQL Injection | `bbq_nosqli` | `POST /api/login` | ✅ gotowe | Błażej |
| 3 | Command Injection | `bbq_cmdi` | do ustalenia | ⬜ do zrobienia | Kuba |
| 4 | Path Traversal | `bbq_pathtraversal` | do ustalenia | ⬜ do zrobienia | Kuba |
| 5 | Arbitrary File Read / Write | `bbq_fileio` | do ustalenia | ⬜ do zrobienia | Wojtek |
| 6 | Race Conditions | `bbq_race` | do ustalenia | ⬜ do zrobienia | Radek |
| 7 | Problem N+1 | `bbq_nplusone` | `GET /api/orders` | ✅ gotowe | Michał |
| 8 | Wielokrotne wykonanie / współbieżność | `bbq_concurrency` | `POST /api/orders` | ✅ gotowe | Michał |
| 9 | Deskryptory plików i gniazd | `bbq_fdleak` | do ustalenia | ⬜ do zrobienia | Patryk |

Legenda: ✅ gotowe · 🟡 w trakcie · ⬜ do zrobienia

Dokumentacja gotowych modułów znajduje się w:

- [SQL Injection](podatnosci/SQLi.md)
- [NoSQL Injection](podatnosci/NoSQLi.md)
- [Problem N+1](podatnosci/Nplusone.md)
- [Współbieżność](podatnosci/Concurrency.md)

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

## Pomysły dla pozostałych modułów

### Command Injection (`bbq_cmdi`)

Endpoint diagnostyczny uruchamiający polecenie systemowe. Wariant poprawiony
powinien używać listy argumentów, bez `shell=True`, oraz whitelisty.

### Path Traversal (`bbq_pathtraversal`)

Endpoint pobierający plik po nazwie. Wariant poprawiony powinien używać
`Path.resolve()` i sprawdzać katalog bazowy.

### Arbitrary File Read / Write (`bbq_fileio`)

Endpoint odczytu/zapisu pliku. Wariant poprawiony powinien ograniczać katalog,
nazwę, rozmiar i typ pliku.

### Race Conditions (`bbq_race`)

Kupon `GRILL10` i produkt z jednym stanem magazynowym. Wariant poprawiony
powinien używać atomowego `UPDATE ... WHERE` albo blokady wiersza.

### Deskryptory plików i gniazd (`bbq_fdleak`)

Endpoint otwierający pliki lub gniazda. Wariant poprawiony powinien używać
context managerów i gwarantować zamknięcie zasobów.

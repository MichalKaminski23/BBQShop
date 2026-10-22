# Plan implementacji

> 📌 **Aktualizuj ten plik na bieżąco.** Gdy skończysz moduł, zmień jego status w tabeli
> (`⬜ do zrobienia` → `🟡 w trakcie` → `✅ gotowe`), wpisz się w kolumnie „Kto", odhacz
> zadania w sekcji danego modułu i ustaw datę. Dzięki temu cała sekcja widzi, co jest zrobione.

## Status modułów

| # | Moduł | Pakiet | Endpoint | Status | Kto |
|---|-------|--------|----------|--------|-----|
| 1 | SQL Injection | `bbq_sqli` | `GET /api/products/search` | ✅ gotowe | — |
| 2 | NoSQL Injection | `bbq_nosqli` | `POST /api/login` | ✅ gotowe | — |
| 3 | Command Injection | `bbq_cmdi` | *(do ustalenia)* | ⬜ do zrobienia | — |
| 4 | Path Traversal | `bbq_pathtraversal` | *(do ustalenia)* | ⬜ do zrobienia | — |
| 5 | Arbitrary File Read / Write | `bbq_fileio` | *(do ustalenia)* | ⬜ do zrobienia | — |
| 6 | Race Conditions | `bbq_race` | *(do ustalenia)* | ⬜ do zrobienia | — |
| 7 | Problem N+1 | `bbq_nplusone` | *(do ustalenia)* | ⬜ do zrobienia | — |
| 8 | Nieograniczona współbieżność / wielokrotne wykonanie | `bbq_concurrency` | *(do ustalenia)* | ⬜ do zrobienia | — |
| 9 | Deskryptory plików i gniazd | `bbq_fdleak` | *(do ustalenia)* | ⬜ do zrobienia | — |

Legenda: ✅ gotowe · 🟡 w trakcie · ⬜ do zrobienia

---

## Jak dodać nowy moduł (wzór: `packages/sqli`)

Każdy moduł ma ten sam układ: wersja podatna w `vulnerable/`, poprawiona w `secure/`, wspólny
interfejs w `repository.py`, router wybierający wariant wg `.env`, testy na obu wersjach.

1. **Skopiuj wzór:** `packages/sqli` → `packages/<nazwa>`, zmień nazwy na `bbq_<nazwa>`.
   Kod podatny do `vulnerable/`, poprawiony do `secure/`.
2. **Zarejestruj moduł** w `packages/<nazwa>/pyproject.toml`:
   ```toml
   [project.entry-points."bbqshop.modules"]
   <nazwa> = "bbq_<nazwa>:module"
   ```
3. **Dodaj paczkę** do głównego `pyproject.toml` (`dependencies`, `[tool.uv.sources]`,
   `[tool.mypy].packages`), potem `uv sync`.
4. **Schemat bazy** – korzystaj ze wspólnego `bbq_db`. Gdyby trzeba było nowej tabeli/kolumny,
   dodaj model w `packages/db/src/bbq_db/models/` i migrację:
   `uv run alembic -c packages/db/alembic.ini revision --autogenerate -m "<opis>"`.
5. **Docker** – dopisz `COPY packages/<nazwa>/pyproject.toml packages/<nazwa>/` w
   [`packages/api/Dockerfile`](../packages/api/Dockerfile).
6. **Konfiguracja** – dodaj `BBQ_MODULE_<NAZWA>` w [`.env.example`](../.env.example).
7. **Testy** – te same scenariusze na obu wariantach (patrz `packages/sqli/tests`
   i `packages/nosqli/tests`): zwykłe działanie w obu, atak przechodzi w `vulnerable`,
   jest zablokowany w `secure`.
8. **README modułu** – krótki opis podatności, przykładowy atak i opis poprawki.

API odkrywa moduł automatycznie (entry points) – nie trzeba zmieniać kodu `bbq_api`.

### Checklista dla każdego modułu
- [ ] Struktura paczki (`vulnerable/`, `secure/`, `repository.py`, `router.py`, `schemas.py`)
- [ ] Wersja podatna działa i da się ją zaatakować
- [ ] Wersja poprawiona blokuje atak, normalne działanie bez zmian
- [ ] Testy jednostkowe + integracyjne (oba warianty)
- [ ] `BBQ_MODULE_<NAZWA>` w `.env.example`, wpis w `Dockerfile`
- [ ] README modułu (atak + poprawka)
- [ ] `uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest` – zielone

---

## Pomysły na implementację pozostałych modułów

> Propozycje punktu zaczepienia – do doprecyzowania przy realizacji. Wiele z nich może
> wykorzystać istniejące tabele (patrz komentarze w [`seed/data.py`](../packages/db/src/bbq_db/seed/data.py)).

### 3. Command Injection (`bbq_cmdi`)
- Endpoint uruchamiający polecenie systemowe z danych użytkownika (np. „diagnostyka": `ping` hosta, konwersja/eksport).
- ❌ Podatna: sklejanie polecenia i `shell=True`. ✅ Poprawiona: brak shella, lista argumentów, walidacja/whitelist.

### 4. Path Traversal (`bbq_pathtraversal`)
- Endpoint pobierający plik po nazwie (np. instrukcja produktu, faktura): `GET /api/files?name=...`.
- ❌ Podatna: doklejanie nazwy do ścieżki (`../../etc/passwd`). ✅ Poprawiona: `Path.resolve()` + sprawdzenie, że wynik jest w dozwolonym katalogu.

### 5. Arbitrary File Read / Write (`bbq_fileio`)
- Odczyt/zapis pliku o ścieżce z danych użytkownika (np. zapis notatki/uploadu).
- ❌ Podatna: ścieżka wprost od użytkownika. ✅ Poprawiona: stały katalog, bezpieczna nazwa, limit rozmiaru i typu.

### 6. Race Conditions (`bbq_race`)
- Gotowe dane: kupon jednorazowy `GRILL10` (`uses_left=1`) i produkt `Grill gazowy Flame 3` (`stock=1`).
- ❌ Podatna: sprawdź-potem-zapisz bez blokady (równoległe żądania zużywają kupon/stan wielokrotnie). ✅ Poprawiona: atomowy `UPDATE ... WHERE uses_left > 0` / blokada wiersza.

### 7. Problem N+1 (`bbq_nplusone`)
- Gotowe dane: `orders` + `order_items`. Endpoint listujący zamówienia z pozycjami.
- ❌ Podatna: osobne zapytanie o pozycje dla każdego zamówienia. ✅ Poprawiona: `selectinload`/`join` – jedno zapytanie.

### 8. Nieograniczona współbieżność / wielokrotne wykonanie (`bbq_concurrency`)
- Wielokrotne złożenie tego samego zamówienia / brak limitu równoległych operacji.
- ❌ Podatna: brak idempotencji i limitu. ✅ Poprawiona: klucz idempotencji, semafor/limit równoległości.

### 9. Deskryptory plików i gniazd (`bbq_fdleak`)
- Operacja otwierająca plik/gniazdo przy każdym żądaniu.
- ❌ Podatna: brak zamknięcia (wyciek deskryptorów). ✅ Poprawiona: `with`/context manager, pula połączeń, zamykanie w `finally`.

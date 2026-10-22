# NoSQL Injection (NoSQLi)

## Co to za podatność

W bazach NoSQL (tu: MongoDB) wartość w filtrze zapytania może być **napisem albo obiektem-operatorem** (`$ne`, `$gt`, `$regex`, …). Jeśli aplikacja wkleja dane użytkownika wprost do filtra bez sprawdzenia typu, atakujący zamiast szukać konkretnej wartości może kazać bazie dopasować „cokolwiek". Baza przestaje odróżniać **dane** od **instrukcji zapytania**.

W BBQShop podatne jest **logowanie**: `POST /api/login`. Użytkownicy są w kolekcji MongoDB `users` (hasła hashowane PBKDF2). Operator w polu loginu/hasła pozwala zalogować się bez znajomości danych.

## Gdzie jest w repo

| Element | Plik |
|---------|------|
| Moduł | [`packages/nosqli/`](../../packages/nosqli/) |
| ❌ Wersja podatna | [`packages/nosqli/src/bbq_nosqli/vulnerable/repository.py`](../../packages/nosqli/src/bbq_nosqli/vulnerable/repository.py) |
| ✅ Wersja poprawiona | [`packages/nosqli/src/bbq_nosqli/secure/repository.py`](../../packages/nosqli/src/bbq_nosqli/secure/repository.py) |
| Endpoint (router) | [`packages/nosqli/src/bbq_nosqli/router.py`](../../packages/nosqli/src/bbq_nosqli/router.py) |
| Cel ataku (kolekcja) | [`packages/db/src/bbq_db/mongo/users.py`](../../packages/db/src/bbq_db/mongo/users.py), dane w [`seed/data.py`](../../packages/db/src/bbq_db/seed/data.py) (`USERS`) |
| Testy | [`packages/nosqli/tests/`](../../packages/nosqli/tests/) |
| Opis modułu | [`packages/nosqli/README.md`](../../packages/nosqli/README.md) |

## Na czym polega błąd

Wersja podatna przyjmuje **surowy JSON** i wkleja wartości wprost do filtra Mongo, bez sprawdzenia, czy to napis:

```python
user = await users.find_one({"username": username})
```

Dla `username = "admin"` baza szuka napisu. Dla `username = {"$ne": null}` ten sam kod wykonuje operator „różne od null" — pasuje do dowolnego dokumentu, więc baza zwraca pierwszego użytkownika (`admin`). Podobnie hasło będące obiektem jest „sprawdzane" operatorem zamiast porównaniem hashy.

## Konta testowe

Kolekcja MongoDB `users` (hasła fikcyjne):

| Login | Hasło | Rola |
|-------|-----------|------|
| `admin` | `Admin123!` | admin |
| `jan` | `grill2026` | customer |
| `anna` | `kielbaska` | customer |

## Jak przetestować ręcznie

### Krok 0 — przygotowanie

1. Upewnij się, że w pliku `.env` (w głównym folderze repo) jest wpis:
   ```
   BBQ_MODULE_NOSQLI=vulnerable
   ```
2. Uruchom aplikację (szczegóły w [URUCHOMIENIE.md](../URUCHOMIENIE.md)), np. całość w Dockerze z głównego folderu repo:
   ```bash
   docker compose up -d
   ```
3. Sprawdź, że moduł działa w wersji podatnej — wejdź na http://localhost:8000/api/modules i znajdź `"name":"nosqli"` z `"variant":"vulnerable"`.

> **Dlaczego atak robimy w Swaggerze, a nie w formularzu?** Formularz logowania na stronie wysyła login i hasło zawsze jako **tekst**, więc nie da się nim wysłać operatora `{"$ne": null}`. Dlatego do ataku używamy Swaggera lub curl, gdzie sami układamy treść żądania (JSON). Formularza użyjemy tylko do pokazania normalnego logowania.

---

### Scenariusz A — normalne logowanie przez stronę (dla porównania)

1. Otwórz w przeglądarce: **http://localhost:5173/login**
2. W pole **Login** wpisz `admin`, w pole **Hasło** wpisz `Admin123!`.
3. Kliknij **Zaloguj**.
4. **Efekt:** komunikat „Zalogowano jako admin (rola: admin)".
5. Spróbuj jeszcze raz z błędnym hasłem (np. `zle`) → zobaczysz błąd „Nieprawidłowy login lub hasło" (API zwraca `401`). Czyli bez poprawnych danych normalnie się nie zalogujesz.

---

### Scenariusz B — atak przez Swagger (logowanie bez hasła)

1. Otwórz w przeglądarce: **http://localhost:8000/docs**
2. Znajdź zieloną sekcję **`POST /api/login`** i kliknij ją, żeby rozwinąć.
3. Kliknij przycisk **Try it out**.
4. W pole **Request body** usuń domyślną zawartość i wklej dokładnie:
   ```json
   {"username": "admin", "password": {"$ne": null}}
   ```
5. Kliknij niebieski przycisk **Execute**.
6. **Efekt:** w sekcji **Response body** zobaczysz `{"username":"admin","role":"admin"}` z kodem `200` — zalogowany jako admin **bez podania hasła**.
7. Spróbuj mocniejszego wariantu — bez znajomości loginu (operator w obu polach zwraca pierwszego użytkownika, czyli `admin`). Wklej i **Execute**:
   ```json
   {"username": {"$ne": null}, "password": {"$ne": null}}
   ```
   Wynik ten sam — sesja admina bez loginu i hasła.

Te same ataki z terminala. **Uwaga na cudzysłowy:** w Windows `cmd` trzeba podwójnych z `\"`, nie apostrofów:

```bash
curl -X POST http://localhost:8000/api/login -H "Content-Type: application/json" -d "{\"username\":{\"$ne\":null},\"password\":{\"$ne\":null}}"
```

---

### Scenariusz C — porównanie z wersją poprawioną

1. W pliku `.env` zmień wpis na:
   ```
   BBQ_MODULE_NOSQLI=secure
   ```
2. Przeładuj samo API (z głównego folderu repo):
   ```bash
   docker compose up -d --force-recreate api
   ```
3. Powtórz Scenariusz B z tym samym payloadem.
4. **Efekt:** zamiast logowania dostaniesz kod `422` — walidacja odrzuca nie-tekstowe pola, operator nie trafia do zapytania. Normalne logowanie (`admin` / `Admin123!`) przez stronę dalej działa.

## Jak to jest naprawione (wersja secure)

- Login i hasło muszą być **tekstem** — model Pydantic `LoginRequest` odrzuca obiekty (operatory) z kodem `422`, a repozytorium dodatkowo sprawdza typ.
- Filtr zawiera tylko nazwę użytkownika; hasło jest weryfikowane osobno przez porównanie hashy w czasie stałym (`verify_password`), nigdy w filtrze zapytania.

## Test automatyczny

```bash
uv run pytest packages/nosqli -v
```

Te same scenariusze na obu wariantach: poprawne dane logują, błędne są odrzucane w obu; payload z operatorem loguje bez danych w `vulnerable` i jest zablokowany w `secure`.

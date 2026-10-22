# SQL Injection (SQLi)

## Co to za podatność

SQL Injection polega na tym, że dane od użytkownika są **sklejane bezpośrednio w treść zapytania SQL**. Apostrof w danych kończy literał tekstowy, a dalsza część wejścia jest interpretowana jako kod SQL. Atakujący może w ten sposób doczytać dane, do których nie ma dostępu (np. przez `UNION SELECT`), ominąć warunki albo zmodyfikować zapytanie.

W BBQShop podatny jest **wyszukiwarka produktów**: `GET /api/products/search?q=<fraza>`. Celem ataku jest tabela `admin_secrets`, której nie zwraca żaden normalny endpoint.

## Gdzie jest w repo

| Element | Plik |
|---------|------|
| Moduł | [`packages/sqli/`](../../packages/sqli/) |
| ❌ Wersja podatna | [`packages/sqli/src/bbq_sqli/vulnerable/repository.py`](../../packages/sqli/src/bbq_sqli/vulnerable/repository.py) |
| ✅ Wersja poprawiona | [`packages/sqli/src/bbq_sqli/secure/repository.py`](../../packages/sqli/src/bbq_sqli/secure/repository.py) |
| Endpoint (router) | [`packages/sqli/src/bbq_sqli/router.py`](../../packages/sqli/src/bbq_sqli/router.py) |
| Cel ataku (tabela) | [`packages/db/src/bbq_db/models/secret.py`](../../packages/db/src/bbq_db/models/secret.py), dane w [`seed/data.py`](../../packages/db/src/bbq_db/seed/data.py) (`SECRETS`) |
| Testy | [`packages/sqli/tests/`](../../packages/sqli/tests/) |
| Opis modułu | [`packages/sqli/README.md`](../../packages/sqli/README.md) |

## Na czym polega błąd

W wersji podatnej fraza wyszukiwania jest wklejana wprost do zapytania:

```python
sql = (
    "SELECT id, name, category, price, description FROM products "
    f"WHERE name ILIKE '%{query}%' ORDER BY id"
)
```

Dla `query = "grill"` zapytanie szuka produktów. Ale dla `query` z apostrofem i `UNION SELECT` baza wykona dodatkowe zapytanie i zwróci dane z innej tabeli.

## Jak przetestować ręcznie

### Krok 0 — przygotowanie

1. Upewnij się, że w pliku `.env` (w głównym folderze repo) jest wpis:
   ```
   BBQ_MODULE_SQLI=vulnerable
   ```
2. Uruchom aplikację (szczegóły w [URUCHOMIENIE.md](../URUCHOMIENIE.md)), np. całość w Dockerze z głównego folderu repo:
   ```bash
   docker compose up -d
   ```
3. Sprawdź, że moduł działa w wersji podatnej — wejdź na http://localhost:8000/api/modules i znajdź `"name":"sqli"` z `"variant":"vulnerable"`.

Payload (fraza wyszukiwania), który będziemy wpisywać w obu scenariuszach:

```
' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--
```

---

### Scenariusz A — przez sklep w przeglądarce (najprościej)

1. Otwórz w przeglądarce: **http://localhost:5173/shop**
2. W pole wyszukiwania (placeholder „Szukaj produktu, np. grill") wpisz najpierw zwykłe `grill` i kliknij **Szukaj** — zobaczysz 3 produkty. To stan normalny.
3. Teraz w to samo pole wklej payload:
   ```
   ' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--
   ```
4. Kliknij **Szukaj**.
5. **Efekt:** na liście pojawią się „produkty" z kategorią `LEAK`, a w miejscu opisu będą **sekrety z tabeli `admin_secrets`** — m.in. `FLAG{sqli_union_select_works}` oraz fikcyjny klucz płatności `sk_test_bbqshop_not_a_real_key`. To dane, których sklep normalnie nie pokazuje.

---

### Scenariusz B — przez Swagger (dokumentacja API)

1. Otwórz w przeglądarce: **http://localhost:8000/docs**
2. Znajdź zieloną sekcję **`GET /api/products/search`** i kliknij ją, żeby rozwinąć.
3. Kliknij przycisk **Try it out** (po prawej).
4. W pole tekstowe parametru **`q`** wklej payload:
   ```
   ' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--
   ```
5. Kliknij niebieski przycisk **Execute**.
6. **Efekt:** zjedź do sekcji **Response body** — zobaczysz rekordy z `"category": "leak"`, a w polu `"description"` wartości sekretów (`FLAG{...}`, klucz płatności).

Ten sam atak z terminala (`-G --data-urlencode` samo koduje znaki specjalne, działa też w Windows `cmd`):

```bash
curl -G "http://localhost:8000/api/products/search" --data-urlencode "q=' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--"
```

---

### Scenariusz C — porównanie z wersją poprawioną

1. W pliku `.env` zmień wpis na:
   ```
   BBQ_MODULE_SQLI=secure
   ```
2. Przeładuj samo API (z głównego folderu repo):
   ```bash
   docker compose up -d --force-recreate api
   ```
3. Powtórz Scenariusz A lub B z tym samym payloadem.
4. **Efekt:** zwykłe wyszukiwanie `grill` dalej działa, ale payload UNION zwraca **pustą listę** (`[]`) — fraza trafia do bazy jako parametr, nie jako kod SQL. Atak nie przechodzi.

## Jak to jest naprawione (wersja secure)

- Zapytanie budowane przez SQLAlchemy; fraza trafia do bazy jako **parametr**, nigdy jako fragment SQL.
- Znaki specjalne wzorca `LIKE` (`%`, `_`) są escapowane.
- Długość frazy ograniczona na poziomie endpointu (walidacja zwraca `422`).

## Test automatyczny

```bash
uv run pytest packages/sqli -v
```

Te same scenariusze uruchamiane na obu wariantach: zwykłe wyszukiwanie działa w obu, payload UNION wycieka sekrety w `vulnerable` i jest zwykłym tekstem (brak wyników) w `secure`.

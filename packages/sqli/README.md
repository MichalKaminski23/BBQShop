# bbq-sqli: SQL Injection

Wyszukiwarka produktów: `GET /api/products/search?q=<fraza>`.

Wariant ustawiasz w `.env`:

```
BBQ_MODULE_SQLI=vulnerable   # vulnerable | secure | off
```

## ❌ Wersja podatna ([vulnerable.py](src/bbq_sqli/vulnerable.py))

Fraza jest wklejana w zapytanie SQL:

```python
f"... WHERE name ILIKE '%{query}%' ORDER BY id"
```

Apostrof kończy literał tekstowy, a dalsza część frazy wykonuje się jako SQL. Dzięki temu można np. dokleić `UNION SELECT` i odczytać tabelę `admin_secrets`, której nie zwraca żaden endpoint.

**Przykładowy atak:**

```
q = ' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--
```

W odpowiedzi pole `description` zawiera wartości z tabeli `admin_secrets`.

## ✅ Wersja poprawiona ([secure.py](src/bbq_sqli/secure.py))

- Zapytanie budowane przez SQLAlchemy. Fraza trafia do bazy jako **parametr**, nigdy jako fragment SQL.
- Znaki `%` i `_` są escapowane, więc wzorzec `LIKE` traktuje je dosłownie.
- Długość frazy jest ograniczona do 100 znaków (walidacja FastAPI zwraca 422).

## Testy

[tests/test_sqli_repositories.py](tests/test_sqli_repositories.py) uruchamia te same scenariusze na obu wariantach:

- zwykłe wyszukiwanie działa w obu,
- payload UNION wycieka sekrety w `vulnerable`,
- ten sam payload w `secure` jest zwykłym tekstem i nic nie zwraca.

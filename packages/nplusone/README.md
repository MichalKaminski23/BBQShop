# bbq-nplusone: problem N+1

Moduł pokazuje problem N+1 na liście zamówień. Endpoint zwraca zamówienia
razem z ich pozycjami:

```text
GET /api/orders
```

W aplikacji frontendowej widok jest dostępny pod adresem:

```text
http://localhost:5173/orders
```

Pełny scenariusz demonstracyjny znajduje się w
[docs/podatnosci/Nplusone.md](../../docs/podatnosci/Nplusone.md). Ten plik
opisuje implementację i testy paczki.

## Wybór wariantu

W pliku `.env` ustaw:

```dotenv
BBQ_MODULE_NPLUSONE=vulnerable   # vulnerable | secure | off
```

Po zmianie konfiguracji przeładuj API:

```powershell
docker compose up -d --force-recreate api
```

## Na czym polega problem

Wariant podatny najpierw pobiera wszystkie zamówienia, a potem wykonuje
osobne zapytanie o pozycje dla każdego zamówienia:

```text
1 zapytanie o zamówienia + N zapytań o pozycje = 1 + N
```

Przy 12 zamówieniach seedowanych przykładowymi danymi endpoint wykona
13 zapytań SQL. Odpowiedź HTTP zawiera te same dane co w wariancie
poprawionym, ale liczba zapytań rośnie wraz z liczbą zamówień.

## Wersja poprawiona

Wariant poprawiony używa `selectinload(Order.items)`. SQLAlchemy pobiera
wszystkie pozycje jednym dodatkowym zapytaniem:

```text
1 zapytanie o zamówienia + 1 zapytanie o pozycje = 2
```

Liczba zapytań nie rośnie liniowo wraz z liczbą zamówień.

## Demonstracja w aplikacji

Włącz diagnostykę zapytań:

```dotenv
BBQ_DB_METRICS=true
```

Następnie uruchom lub przebuduj aplikację:

```powershell
docker compose up --build -d
```

Otwórz [http://localhost:5173/orders](http://localhost:5173/orders).
Widok pokazuje:

- zamówienia i ich pozycje,
- aktywny wariant modułu,
- rzeczywistą liczbę zapytań SQL,
- łączny czas wykonania zapytań SQL.

Diagnostyka jest również dostępna w nagłówkach odpowiedzi:

```text
X-SQL-Query-Count
X-SQL-Query-Time-Ms
```

Można ją obserwować w DevTools przeglądarki w zakładce **Network** albo
w logach API:

```powershell
docker compose logs -f --tail=0 api
```

`BBQ_DB_METRICS` jest wyłączone domyślnie w `.env.example`, ponieważ
szczegółowe metryki SQL są przeznaczone do demonstracji i diagnostyki,
nie do ujawniania w publicznej aplikacji.

## Dane testowe

Zamówienia są zdefiniowane w
[`packages/db/src/bbq_db/seed/data.py`](../db/src/bbq_db/seed/data.py).
Seed działa tylko dla pustych tabel. Jeśli baza została już uruchomiona
wcześniej, aby odtworzyć wszystkie dane od zera:

```powershell
docker compose down -v
docker compose up --build -d
```

> `docker compose down -v` usuwa lokalne wolumeny baz danych.

## Testy

Uruchom testy modułu:

```powershell
uv run pytest packages/nplusone -v
```

Testy sprawdzają, że:

- wariant `vulnerable` wykonuje `1 + N` zapytań,
- wariant `secure` wykonuje dokładnie 2 zapytania,
- nagłówki diagnostyczne zawierają liczbę i czas zapytań.

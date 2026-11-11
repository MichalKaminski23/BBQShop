# Problem N+1

## Co to za problem

Problem N+1 występuje, gdy aplikacja najpierw pobiera listę rekordów jednym
zapytaniem, a następnie wykonuje kolejne zapytanie dla każdego elementu tej
listy. Przy `N` zamówieniach daje to `1 + N` zapytań zamiast stałej liczby.

W BBQShop problem pokazuje lista zamówień:

```text
GET /api/orders
```

Frontend udostępnia ten endpoint na stronie:

```text
http://localhost:5173/orders
```

## Gdzie jest w repozytorium

| Element | Plik |
|---------|------|
| Moduł | [`packages/nplusone/`](../../packages/nplusone/) |
| Wersja podatna | [`vulnerable/repository.py`](../../packages/nplusone/src/bbq_nplusone/vulnerable/repository.py) |
| Wersja poprawiona | [`secure/repository.py`](../../packages/nplusone/src/bbq_nplusone/secure/repository.py) |
| Router | [`router.py`](../../packages/nplusone/src/bbq_nplusone/router.py) |
| Modele zamówień | [`order.py`](../../packages/db/src/bbq_db/models/order.py) |
| Dane przykładowe | [`seed/data.py`](../../packages/db/src/bbq_db/seed/data.py) |
| Metryki SQL | [`db.py`](../../packages/core/src/bbq_core/db.py) |
| Testy | [`packages/nplusone/tests/`](../../packages/nplusone/tests/) |
| Dokumentacja modułu | [`packages/nplusone/README.md`](../../packages/nplusone/README.md) |

## Wersja podatna

Wariant `vulnerable` pobiera zamówienia, a następnie w pętli wykonuje
zapytanie o pozycje każdego zamówienia:

```python
orders = await session.scalars(select(Order).order_by(Order.id))
for order in orders:
    items = await session.scalars(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
```

Dla 12 zamówień oznacza to:

```text
1 + 12 = 13 zapytań SQL
```

## Wersja poprawiona

Wariant `secure` używa eager loadingu:

```python
select(Order).options(selectinload(Order.items))
```

SQLAlchemy wykonuje jedno zapytanie o zamówienia i jedno zapytanie o
pozycje wszystkich zamówień:

```text
2 zapytania SQL niezależnie od liczby zamówień
```

Odpowiedź endpointu jest taka sama w obu wariantach. Różnica dotyczy
wewnętrznego sposobu pobierania danych i staje się istotna przy większej
liczbie rekordów.

## Demonstracja krok po kroku

### 1. Włącz diagnostykę

W `.env` ustaw:

```dotenv
BBQ_MODULE_NPLUSONE=vulnerable
BBQ_DB_METRICS=true
```

Uruchom aplikację:

```powershell
docker compose up --build -d
```

Jeżeli chcesz mieć pełny, świeży seed danych:

```powershell
docker compose down -v
docker compose up --build -d
```

### 2. Otwórz widok zamówień

Wejdź na:

```text
http://localhost:5173/orders
```

Frontend pokaże rzeczywistą liczbę zapytań i ich łączny czas. Te same
wartości są dostępne w nagłówkach odpowiedzi:

```text
X-SQL-Query-Count: 13
X-SQL-Query-Time-Ms: 8.42
```

Nagłówki można zobaczyć w DevTools przeglądarki:
**Network → orders → Headers**.

### 3. Porównaj wariant poprawiony

Zmień w `.env`:

```dotenv
BBQ_MODULE_NPLUSONE=secure
```

Przeładuj API:

```powershell
docker compose up -d --force-recreate api
```

Odśwież stronę `/orders`. Liczba zapytań powinna zmienić się z `13` na
`2`. Czas może się różnić między uruchomieniami, ponieważ zależy między
innymi od obciążenia i cache bazy.

### 4. Logi SQL

Przy `BBQ_DB_METRICS=true` logowanie SQL jest włączone. Możesz obserwować
je poleceniem:

```powershell
docker compose logs -f --tail=0 api
```

W wariancie podatnym zobaczysz powtarzające się zapytania do
`order_items` z różnymi identyfikatorami zamówień. W wariancie poprawionym
zobaczysz jedno zapytanie z warunkiem `IN (...)`.

## Automatyczna weryfikacja

```powershell
uv run pytest packages/nplusone -v
```

Testy mierzą liczbę zapytań przez event SQLAlchemy
`before_cursor_execute`/`after_cursor_execute` i sprawdzają zarówno
repozytoria, jak i nagłówki HTTP.

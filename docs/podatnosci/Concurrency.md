# Nieograniczona współbieżność i wielokrotne wykonanie operacji

## Co to za problem

Jeśli endpoint wykonujący operację biznesową nie ma idempotencji ani limitu
równoległości, to ponowienie żądania może wykonać operację ponownie. Źródłem
powtórzenia może być podwójne kliknięcie, retry klienta albo równoległe
żądania wysłane przez atakującego.

W BBQShop problem pokazuje składanie zamówienia:

```text
POST /api/orders
```

Frontendowy formularz demonstracyjny znajduje się pod adresem:

```text
http://localhost:5173/concurrency
```

## Gdzie jest w repozytorium

| Element | Plik |
|---------|------|
| Moduł | [`packages/concurrency/`](../../packages/concurrency/) |
| Wersja podatna | [`vulnerable/repository.py`](../../packages/concurrency/src/bbq_concurrency/vulnerable/repository.py) |
| Wersja poprawiona | [`secure/repository.py`](../../packages/concurrency/src/bbq_concurrency/secure/repository.py) |
| Router | [`router.py`](../../packages/concurrency/src/bbq_concurrency/router.py) |
| Model zamówienia | [`order.py`](../../packages/db/src/bbq_db/models/order.py) |
| Migracja | [`0001_shop_schema.py`](../../packages/db/src/bbq_db/migrations/versions/0001_shop_schema.py) |
| Testy | [`packages/concurrency/tests/`](../../packages/concurrency/tests/) |
| Dokumentacja modułu | [`packages/concurrency/README.md`](../../packages/concurrency/README.md) |

## Wersja podatna

Wariant podatny ignoruje `Idempotency-Key` i zawsze tworzy nowe zamówienie.
Osiem identycznych żądań może więc utworzyć osiem rekordów.

## Wersja poprawiona

Wariant poprawiony używa kilku zabezpieczeń:

1. Klient musi przesłać `Idempotency-Key`.
2. Klucz jest zapisywany w kolumnie `orders.idempotency_key`.
3. Kolumna ma ograniczenie `UNIQUE`.
4. Ponowienie tego samego żądania zwraca istniejące zamówienie.
5. Semafor ogranicza liczbę równoczesnych operacji w procesie do 4.
6. Błąd unikalności powstały w wyścigu jest obsługiwany przez ponowne
   odczytanie istniejącego zamówienia.

Semafor ogranicza obciążenie pojedynczego procesu aplikacji, natomiast
unikalny klucz idempotencji zapewnia ochronę przed powtórzeniem również
przy równoległych żądaniach.

## Demonstracja

### Konfiguracja

W `.env` ustaw:

```dotenv
BBQ_MODULE_CONCURRENCY=vulnerable
```

Uruchom aplikację:

```powershell
docker compose up --build -d
```

### Pojedyncze powtórzenie

Otwórz http://localhost:8000/docs i użyj `POST /api/orders` z nagłówkiem:

```text
Idempotency-Key: demo-key-1
```

oraz treścią:

```json
{
  "customer_name": "Demo",
  "items": [{"product_id": 1, "quantity": 1}]
}
```

Wyślij żądanie dwa razy. W `vulnerable` powstaną dwa różne zamówienia.
Po zmianie na `BBQ_MODULE_CONCURRENCY=secure` drugie żądanie zwróci
wcześniej utworzone zamówienie.

### Równoległe żądania

Test automatyczny wykonuje 8 identycznych requestów:

```powershell
uv run pytest packages/concurrency/tests/test_concurrency_app.py -v
```

Oczekiwany wynik:

```text
vulnerable: 8 różnych zamówień
secure:     1 zamówienie
```

## Ograniczenia demonstracji

Semafor jest ograniczeniem lokalnym dla jednego procesu aplikacji. W
środowisku wieloprocesowym lub po uruchomieniu wielu instancji nie zastępuje
mechanizmu opartego o bazę danych. Dlatego najważniejszym zabezpieczeniem
jest trwały, unikalny klucz idempotencji.

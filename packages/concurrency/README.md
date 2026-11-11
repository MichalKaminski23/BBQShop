# bbq-concurrency: nieograniczona współbieżność i wielokrotne wykonanie

Moduł pokazuje problem wielokrotnego wykonania tej samej operacji na
przykładzie składania zamówienia:

```text
POST /api/orders
```

W aplikacji frontendowej formularz demonstracyjny jest dostępny pod adresem:

```text
http://localhost:5173/concurrency
```

Pełny scenariusz demonstracyjny znajduje się w
[docs/podatnosci/Concurrency.md](../../docs/podatnosci/Concurrency.md). Ten
plik opisuje implementację i testy paczki.

## Wybór wariantu

W pliku `.env` ustaw:

```dotenv
BBQ_MODULE_CONCURRENCY=vulnerable   # vulnerable | secure | off
```

Po zmianie konfiguracji przeładuj API:

```powershell
docker compose up -d --force-recreate api
```

## Wersja podatna

Wariant `vulnerable` ignoruje nagłówek `Idempotency-Key`. Każde powtórzenie
żądania tworzy nowe zamówienie, również gdy kilka identycznych żądań
przychodzi równocześnie.

W prawdziwej aplikacji klient może ponowić żądanie po timeoutcie, a
użytkownik może kliknąć przycisk kilka razy. Bez idempotencji ta sama
operacja może zostać wykonana wielokrotnie.

## Wersja poprawiona

Wariant `secure`:

- wymaga nagłówka `Idempotency-Key`,
- zapisuje klucz razem z zamówieniem,
- zwraca wcześniej utworzone zamówienie przy ponowieniu tego samego żądania,
- ogranicza liczbę równoczesnych operacji semaforem do 4,
- korzysta z unikalnego indeksu `orders.idempotency_key`, więc działa również
  przy wyścigu pomiędzy równoległymi żądaniami.

Ponowienie tego samego żądania zwraca `200`, a pierwsze wykonanie `201`.

## Przykład żądania

```json
{
  "customer_name": "Test concurrency",
  "items": [
    {
      "product_id": 1,
      "quantity": 1
    }
  ]
}
```

Nagłówek:

```text
Idempotency-Key: demo-key-1
```

## Demonstracja przez Swagger

1. Ustaw `BBQ_MODULE_CONCURRENCY=vulnerable`.
2. Uruchom aplikację:

   ```powershell
   docker compose up --build -d
   ```

3. Otwórz http://localhost:8000/docs.
4. Wybierz `POST /api/orders`, kliknij **Try it out** i wyślij żądanie.
5. Wyślij je ponownie z tym samym `Idempotency-Key`.
6. W wariancie podatnym oba żądania utworzą różne zamówienia.
7. Ustaw `BBQ_MODULE_CONCURRENCY=secure` i przeładuj API:

   ```powershell
   docker compose up -d --force-recreate api
   ```

8. Wyślij to samo żądanie ponownie. Wariant poprawiony zwróci to samo
   zamówienie zamiast tworzyć kolejne.

## Demonstracja równoległa

W PowerShell można wysłać kilka requestów równocześnie:

```powershell
$body = @{
  customer_name = "Parallel demo"
  items = @(@{ product_id = 1; quantity = 1 })
} | ConvertTo-Json -Depth 3

1..8 | ForEach-Object -Parallel {
  Invoke-RestMethod `
    -Uri "http://localhost:8000/api/orders" `
    -Method Post `
    -Headers @{ "Idempotency-Key" = "parallel-demo" } `
    -ContentType "application/json" `
    -Body $using:body
} -ThrottleLimit 8
```

W `vulnerable` powstanie 8 zamówień. W `secure` wszystkie odpowiedzi
wskażą jedno zamówienie.

## Testy

```powershell
uv run pytest packages/concurrency -v
```

Testy wysyłają 8 równoległych, identycznych żądań i sprawdzają oba warianty.

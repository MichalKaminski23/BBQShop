# bbq-fdleak: deskryptory plików i gniazd

Moduł pokazuje problem niepoprawnego zarządzania deskryptorami plików i gniazd.
Wersja demonstracyjna działa na `/dev/null` i tworzy lokalne połączenia TCP
loopback z krótką transmisją danych. Nie odczytuje plików użytkownika ani nie
łączy się z zewnętrzną siecią.

Frontendowy formularz jest dostępny pod adresem:

```text
http://localhost:5173/fdleak
```

Endpointy API:

- `GET /api/fdleak/file?count=5`
- `GET /api/fdleak/socket?count=5`

Liczba zasobów na żądanie jest ograniczona do 1–100.

## Warianty

- `vulnerable` – zapisuje otwarte uchwyty w repozytorium i pozostawia je
  otwarte po odpowiedzi.
- `secure` – zamyka pliki i gniazda przez context managery.

Wynik pokazuje również `outstanding_count` — narastającą liczbę pozostawionych
otwartych zasobów danego typu w procesie API. W wariancie podatnym licznik
wzrasta po każdym żądaniu; w poprawionym pozostaje równy zero.

Wariant podatny zajmuje deskryptory procesu API do czasu jego restartu.
Z tego powodu moduł należy uruchamiać wyłącznie lokalnie lub w odizolowanym
środowisku edukacyjnym. Po demonstracji zrestartuj API.

Szczegółowa instrukcja znajduje się w
[docs/podatnosci/FdLeak.md](../../docs/podatnosci/FdLeak.md).

Testy:

```powershell
uv run pytest packages/fdleak/tests -v
```

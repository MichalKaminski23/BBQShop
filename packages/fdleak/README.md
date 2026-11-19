# bbq-fdleak: deskryptory plików i gniazd

Moduł ma prezentować problem niepoprawnego zarządzania otwartymi zasobami
systemowymi:

- otwieranie plików bez gwarancji ich zamknięcia,
- tworzenie gniazd bez gwarancji ich zamknięcia,
- utrzymywanie zasobów po zakończeniu operacji,
- skutki wielokrotnego powtarzania tych operacji.

## Warianty

- `vulnerable` – celowo pozostawia zasoby otwarte.
- `secure` – zamyka zasoby przez context manager albo blokę `finally`.

## Plan endpointów

- `GET /api/fdleak/file`
- `GET /api/fdleak/socket`

Szczegółowa implementacja i instrukcja demonstracji zostaną dodane w kolejnych
etapach.

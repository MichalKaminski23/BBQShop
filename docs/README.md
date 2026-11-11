# Dokumentacja BBQShop

To jest główny indeks dokumentacji projektu. Zacznij od instrukcji
uruchomienia, a następnie przejdź do opisu konkretnej podatności.

## Szybki start

- [Uruchomienie i codzienna praca](URUCHOMIENIE.md)
- [Plan i status modułów](PLAN.md)
- [Diagram architektury](architecture.svg)

## Demonstracje podatności

| Temat | Moduł | Endpoint | Instrukcja |
|---|---|---|---|
| SQL Injection | `bbq_sqli` | `GET /api/products/search` | [SQLi.md](podatnosci/SQLi.md) |
| NoSQL Injection | `bbq_nosqli` | `POST /api/login` | [NoSQLi.md](podatnosci/NoSQLi.md) |
| Problem N+1 | `bbq_nplusone` | `GET /api/orders` | [Nplusone.md](podatnosci/Nplusone.md) |
| Wielokrotne wykonanie i współbieżność | `bbq_concurrency` | `POST /api/orders` | [Concurrency.md](podatnosci/Concurrency.md) |

Pozostałe moduły są jeszcze w planie i pojawią się tutaj po implementacji.

## Zasada organizacji dokumentacji

- [URUCHOMIENIE.md](URUCHOMIENIE.md) zawiera tylko wspólne komendy:
  instalację, start, zatrzymywanie, konfigurację, testy i reset danych.
- [PLAN.md](PLAN.md) zawiera status prac i checklistę dodawania modułu.
- `docs/podatnosci/*.md` zawiera instrukcję demonstracji konkretnego tematu.
- `packages/*/README.md` zawiera techniczny opis konkretnej paczki i jej kodu.
- [README.md](../README.md) zawiera krótki opis projektu i odsyła tutaj.

Jeżeli zmiana dotyczy tylko jednego modułu, aktualizuj przede wszystkim jego
plik w `docs/podatnosci/` oraz `packages/<moduł>/README.md`. Wspólne komendy
zmieniaj wyłącznie w [URUCHOMIENIE.md](URUCHOMIENIE.md).

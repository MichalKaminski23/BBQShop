# BBQShop

Aplikacja webowa imitująca sklep z produktami na grilla. W aplikacji **celowo umieszczono podatności**. Każda z nich ma też **poprawioną (bezpieczną) wersję kodu**, żeby obie wersje dało się porównać i przetestować.

> ⚠️ **Uwaga:** projekt jest celowo podatny i służy wyłącznie do celów edukacyjnych (przedmiot TBO). Nie uruchamiaj go w środowisku produkcyjnym ani nie wystawiaj publicznie do internetu.

## Skład sekcji

- Michał Kamiński
- Błażej Sztefka
- Jakub Gnela
- Patryk Czakon
- Wojciech Kierat
- Radosław Rajda

## Technologie

| Warstwa      | Technologia            |
|--------------|------------------------|
| Backend      | Python (FastAPI)       |
| Frontend     | React                  |
| Bazy danych  | PostgreSQL, MongoDB    |

## Podatności

Każda podatność występuje w dwóch wariantach: **podatnym** i **poprawionym**.

| # | Podatność                                                     |
|---|---------------------------------------------------------------|
| 1 | SQL Injection (SQLi)                                          |
| 2 | NoSQL Injection (NoSQLi)                                      |
| 3 | Command Injection                                             |
| 4 | Path Traversal                                                |
| 5 | Arbitrary File Read / Write                                   |
| 6 | Race Conditions                                               |
| 7 | Problem N+1                                                   |
| 8 | Nieograniczona współbieżność / wielokrotne wykonanie operacji |
| 9 | Niepoprawne zarządzanie deskryptorami plików i gniazd         |

## Architektura (założenia)

Zgodnie z uwagami z 19.10:

- Projekt jest podzielony na **osobne paczki (moduły Pythonowe)**, po jednej na każdą podatność lub grupę podatności (np. paczka dla SQLi, paczka dla N+1 itd.). Każda paczka to mniejszy, niezależny projekt.
- **FastAPI** pełni rolę warstwy łączącej moduły i wystawia ich funkcje przez API dla frontendu w React.
- Każdy moduł ma **testy automatyczne** (jednostkowe i inne), które sprawdzają zarówno wersję podatną, jak i poprawioną.

## Repozytorium

https://github.com/MichalKaminski23/BBQShop

## Harmonogram

| Data  | Wydarzenie                                                          |
|-------|---------------------------------------------------------------------|
| 19.10 | Uwagi do projektu: podział na moduły, testy, FastAPI jako warstwa łącząca |
| 02.11 | Spotkanie (zdalnie)                                                 |

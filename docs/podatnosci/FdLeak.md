# Niepoprawne zarządzanie deskryptorami plików i gniazd

## Problem

Deskryptor jest uchwytem do zasobu systemowego, takiego jak otwarty plik lub
gniazdo. Jeśli aplikacja nie zamknie go po użyciu, zasób może pozostać zajęty
aż do zakończenia procesu. Powtarzanie takiej operacji stopniowo zużywa pulę
deskryptorów dostępnych dla procesu.

Demonstracja otwiera pliki `/dev/null` i niepołączone gniazda TCP. Nie czyta
plików użytkownika ani nie wysyła ruchu sieciowego.

## Frontend

Otwórz:

```text
http://localhost:5173/fdleak
```

Wybierz liczbę zasobów od 1 do 100, a następnie użyj przycisku **Otwórz pliki**
lub **Otwórz gniazda**. Odpowiedź pokazuje liczbę otwartych i zamkniętych
zasobów. Możesz powtórzyć żądanie, aby zwiększyć liczbę utrzymywanych
deskryptorów w wariancie podatnym.

## Wybór wariantu

W pliku `.env` ustaw:

```dotenv
BBQ_MODULE_FDLEAK=vulnerable
```

Uruchom lub przebuduj aplikację:

```powershell
docker compose up --build -d
```

Wariant `vulnerable` raportuje `closed_count: 0`; otwarte uchwyty pozostają
przechowywane w procesie API. Wariant `secure` raportuje tyle samo zamkniętych
co otwartych zasobów.

Po demonstracji podatnej wersji zrestartuj API, żeby zwolnić pozostawione
zasoby:

```powershell
docker compose restart api
```

## Endpointy API

- `GET /api/fdleak/file?count=5`
- `GET /api/fdleak/socket?count=5`

Parametr `count` jest ograniczony do zakresu 1–100. Nie zwiększaj limitu ani
nie uruchamiaj demonstracji na publicznie dostępnym API.

## Implementacja

| Element | Plik |
|---|---|
| Router | [`router.py`](../../packages/fdleak/src/bbq_fdleak/router.py) |
| Wspólny kontrakt | [`repository.py`](../../packages/fdleak/src/bbq_fdleak/repository.py) |
| Wariant podatny | [`vulnerable/repository.py`](../../packages/fdleak/src/bbq_fdleak/vulnerable/repository.py) |
| Wariant poprawiony | [`secure/repository.py`](../../packages/fdleak/src/bbq_fdleak/secure/repository.py) |
| Testy | [`packages/fdleak/tests/`](../../packages/fdleak/tests/) |

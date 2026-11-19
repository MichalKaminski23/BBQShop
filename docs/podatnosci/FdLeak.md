# Niepoprawne zarządzanie deskryptorami plików i gniazd

## Problem

Deskryptor jest uchwytem do zasobu systemowego, takiego jak otwarty plik lub
gniazdo. Jeśli aplikacja nie zamknie go po użyciu, zasób może pozostać zajęty
aż do zakończenia procesu. Powtarzanie takiej operacji stopniowo zużywa pulę
deskryptorów dostępnych dla procesu.

Demonstracja otwiera pliki `/dev/null` i tworzy lokalne połączenia TCP
loopback. Każde połączenie przesyła krótki znacznik `bbq-fdleak-demo`, więc
można obserwować rzeczywiste zestawianie połączeń i ruch TCP. Moduł nie czyta
plików użytkownika ani nie łączy się z zewnętrzną siecią.

## Frontend

Otwórz:

```text
http://localhost:5173/fdleak
```

Wybierz liczbę zasobów od 1 do 100, a następnie użyj przycisku **Otwórz pliki**
lub **Otwórz gniazda**. Odpowiedź pokazuje liczbę otwartych i zamkniętych
zasobów. Możesz powtórzyć żądanie, aby zwiększyć liczbę utrzymywanych
deskryptorów w wariancie podatnym.

Pole **Pozostawione otwarte w tym procesie** rośnie po każdym żądaniu
w wariancie podatnym. W wariancie poprawionym pozostaje równe zero.

Przy gniazdach każde żądanie tworzy lokalne połączenia TCP. W `vulnerable`
połączenia pozostają w stanie `ESTABLISHED`; w `secure` są zamykane po
przesłaniu znacznika.

## Sprawdzanie deskryptorów w kontenerze

Poniższe polecenia uruchamiaj z katalogu głównego repozytorium.

### Gniazda

```powershell
docker compose exec api sh -c "grep ' 01 ' /proc/net/tcp"
```

Wpisy ze stanem `01` oznaczają połączenia `ESTABLISHED`. W wynikach będą
również normalne połączenia API z PostgreSQL i MongoDB. Połączenia utworzone
przez demonstrację mają adres loopback `127.0.0.1`, zapisywany w
`/proc/net/tcp` jako `0100007F`.

- `vulnerable`: po kliknięciu **Otwórz gniazda** wpisy loopback `0100007F`
  pozostają aktywne,
- `secure`: połączenia demonstracyjne są zamykane; wpisy mogą chwilowo
  występować jako `TIME_WAIT` (stan `06`), ale nie powinny pozostawać jako
  `ESTABLISHED` (`01`).

Wpisy połączeń baz danych są prawidłowe i nie oznaczają wycieku modułu.

### Pliki

```powershell
docker compose exec api sh -c "find /proc/[0-9]*/fd -lname /dev/null 2>/dev/null"
```

Każda linia wskazuje deskryptor procesu prowadzący do `/dev/null`. Wariant
`vulnerable` otwiera dodatkowe pliki i przechowuje je w procesie API, dlatego
liczba wpisów rośnie po kolejnych kliknięciach **Otwórz pliki**. Wariant
`secure` zamyka pliki natychmiast, więc liczba pozostaje zasadniczo stała.

Niektóre wpisy `/dev/null` mogą należeć do standardowych deskryptorów procesu,
dlatego porównuj wynik przed i po demonstracji. Po demonstracji wariantu
`vulnerable` wykonaj:

```powershell
docker compose restart api
```

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

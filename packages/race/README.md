# Race Conditions

Moduł pokazuje wyścig TOCTOU podczas wykorzystania jednorazowego kuponu
`GRILL10`. Kupon ma 10% rabatu i jedno dostępne użycie. Strona demonstracyjna
jest dostępna pod `/promocje`.

## Demonstracja na stronie

Panel koszyka pokazuje przykładową cenę bazową 100 zł. Każde zaakceptowane
wykorzystanie kuponu nalicza w tej demonstracji rabat 10 zł, a cena końcowa
jest ograniczona do 0 zł. To wizualizacja skutku wyścigu, nie zapis zamówienia.

Przycisk **Wykorzystaj kupon** wysyła pojedyncze żądanie. Przycisk
**Symuluj 20 równoczesnych użyć** wysyła 20 żądań do API i wylicza cenę na
podstawie odpowiedzi `200`. Odpowiedzi `409` są normalnym odrzuceniem żądania;
błędy sieciowe i serwera są pokazywane jako niepełna symulacja. W `secure`
powinno zostać zaakceptowane jedno żądanie, więc cena wyniesie 90 zł. W
`vulnerable` zwykle zostanie zaakceptowanych kilka żądań, a przy co najmniej
10 sukcesach cena spadnie do 0 zł. Wynik `vulnerable` zależy od współbieżności
i obciążenia, dlatego użyj własnego detektora, by wykonać powtarzane serie.

Przycisk **Resetuj kupon** przywraca kupon w bazie i czyści wynik wyświetlany
przez bieżącą stronę. Reset nie zapisuje ani nie usuwa zamówień.

## Wybór wariantu

W pliku `.env` ustaw jedną wartość:

```dotenv
BBQ_MODULE_RACE=vulnerable
```

Po zmianie wariantu uruchom ponownie API, aby wczytało nową konfigurację.
Ustawienie `vulnerable` pokazuje błąd, a `secure` go naprawia:

```dotenv
BBQ_MODULE_RACE=secure
```

Nie zmieniaj pozostałych flag modułów. Wariant możesz sprawdzić na stronie
`/promocje` lub przez `GET /api/modules`.

## Test własnym detektorem

Uruchom z katalogu głównego projektu:

```sh
uv run python packages/race/tools/race_detector.py
```

Detektor sam przywraca `GRILL10` do jednego użycia przed każdą z pięciu serii.
Każda seria wysyła 20 równoczesnych żądań do API i sprawdza, ile z nich zostało
zaakceptowanych.

Wariant `vulnerable` powinien zakończyć się wynikiem `VULNERABLE`, bo więcej niż
jedno żądanie wykorzysta ten sam kupon. Wariant `secure` powinien dać
`NO_RACE_OBSERVED`: jedno żądanie otrzyma `200`, a pozostałe `409`.
`INCONCLUSIVE` oznacza problem z połączeniem, resetem danych lub odpowiedziami
serwera — nie jest dowodem bezpieczeństwa.

Przykładowe wyniki:

```text
Wynik: VULNERABLE
Seria 1: accepted=15, HTTP={'200': 15, '409': 5}, valid=True
```

```text
Wynik: NO_RACE_OBSERVED
Seria 1: accepted=1, HTTP={'409': 19, '200': 1}, valid=True
```

Kolejność kodów w raporcie może być inna. Liczby `accepted` i kody odpowiedzi
pokazują istotny wynik.

## Race The Web

Race The Web to osobne narzędzie CLI, nie jest instalowane razem z BBQShop.
Pobierz wydanie pasujące do systemu z [oficjalnej strony wydań](https://github.com/TheHackerDev/race-the-web/releases/tag/2.0.1)
i rozpakuj plik wykonywalny. Na macOS możesz pobrać wydanie x86_64 i zainstalować
je tak:

```sh
mkdir -p ~/.local/bin
curl -L -o /tmp/race-the-web.zip https://github.com/TheHackerDev/race-the-web/releases/download/2.0.1/race-the-web_2.0.1_osx64.app.zip
unzip -o /tmp/race-the-web.zip -d ~/.local/bin
mv ~/.local/bin/race-the-web_2.0.1_osx64.app ~/.local/bin/race-the-web
chmod +x ~/.local/bin/race-the-web
```

Na Apple Silicon to wydanie x86_64 wymaga Rosetty. Dla innego systemu pobierz
odpowiedni plik z tej samej strony wydań, rozpakuj go i uruchom zgodnie z nazwą
pliku.

Opcjonalna konfiguracja jest w [`tools/race-the-web.toml`](tools/race-the-web.toml).
Uruchom narzędzie, gdy jest zainstalowane i API działa:

```sh
~/.local/bin/race-the-web packages/race/tools/race-the-web.toml
```

Race The Web wysyła równoczesne żądania i grupuje odpowiedzi. Nie sprawdza sam
reguły biznesowej kuponu — robi to `packages/race/tools/race_detector.py`.
Przed każdym uruchomieniem przywróć kupon przyciskiem **Resetuj kupon** na
stronie `/promocje`.

Poniżej są krótkie wycinki surowego outputu z Race The Web 2.0.1. Pominąłem
powtarzające się linie `[DEBUG]`, nagłówki HTTP i drugie wydrukowanie `Unique
Responses`, żeby łatwo było porównać odpowiedzi. Liczba `Similar` pochodzi
bezpośrednio z outputu narzędzia.

`vulnerable` — 15 odpowiedzi sukcesu i 5 konfliktów:

```text
[Status Code] 200
[Body]
{"code":"GRILL10","discount_percent":10,"uses_left":0,"message":"Kupon został wykorzystany."}
Similar: 14

[Status Code] 409
[Body]
{"detail":"Kupon został już wykorzystany."}
Similar: 4
```

`secure` — 1 odpowiedź sukcesu i 19 konfliktów:

```text
[Status Code] 200
[Body]
{"code":"GRILL10","discount_percent":10,"uses_left":0,"message":"Kupon został wykorzystany."}
Similar: 0

[Status Code] 409
[Body]
{"detail":"Kupon został już wykorzystany."}
Similar: 18
```

| Wariant | HTTP 200 | HTTP 409 | Znaczenie wyniku Race The Web |
| --- | ---: | ---: | --- |
| `vulnerable` | 15 | 5 | `200 Similar: 14`, `409 Similar: 4` |
| `secure` | 1 | 19 | `200 Similar: 0`, `409 Similar: 18` |

Race The Web pokazuje jedną przykładową odpowiedź i liczbę podobnych odpowiedzi.
Dlatego `Similar: 14` przy `200` oznacza 15 zaakceptowanych żądań (przykład + 14
podobnych), a `Similar: 18` przy `409` oznacza 19 odrzuconych żądań. To narusza
limit kuponu w `vulnerable`; w `secure` dokładnie jedno żądanie otrzymuje `200`.

## Gdzie znajduje się podatność

### Wariant vulnerable

W [`vulnerable/repository.py`](src/bbq_race/vulnerable/repository.py#L20) najpierw
pobierany i sprawdzany jest kupon, a dopiero potem aktualizowany:

```python
coupon = await self._session.scalar(select(Coupon).where(Coupon.code == code))
if coupon is None or coupon.uses_left <= 0:
    return None

await asyncio.sleep(0.15)
coupon.uses_left -= 1
await self._session.commit()
```

Równoczesne żądania mogą oba odczytać `uses_left == 1` i przejść warunek, zanim
którekolwiek zapisze zmianę. Opóźnienie 150 ms tylko uwidacznia wyścig; jego
źródłem jest rozdzielenie sprawdzenia i aktualizacji.

### Wariant secure

W [`secure/repository.py`](src/bbq_race/secure/repository.py#L18) sprawdzenie
limitu i zmniejszenie licznika są jednym warunkowym poleceniem SQL:

```python
result = await self._session.execute(
    update(Coupon)
    .where(Coupon.code == code, Coupon.uses_left > 0)
    .values(uses_left=Coupon.uses_left - 1)
    .returning(Coupon.discount_percent, Coupon.uses_left)
)
redeemed = result.one_or_none()
if redeemed is None:
    await self._session.rollback()
    return None

await self._session.commit()
```

PostgreSQL atomowo aktualizuje tylko wiersz, który nadal ma dostępne użycie.
Z kolejnych równoczesnych żądań żadne nie otrzyma wiersza z `RETURNING`, więc API
zwróci `409`. Transakcja jest zatwierdzana po uzyskaniu wyniku.

Router wybiera implementację w [`router.py`](src/bbq_race/router.py#L12).
Detektor resetuje wyłącznie `GRILL10` w [`race_detector.py`](tools/race_detector.py#L44),
a potem wysyła równoczesne żądania HTTP.

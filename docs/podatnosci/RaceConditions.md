# Race Condition: wykorzystanie jednorazowego kuponu

Moduł `bbq_race` wykorzystuje istniejącą tabelę `coupons` i rekord `GRILL10`.
Endpoint `POST /api/race/coupons/redeem` otrzymuje `{"code":"GRILL10"}`.

Pełna instrukcja uruchomienia, polecenia detektora i Race The Web oraz zapisane
wyniki obu wariantów są w [README modułu](../../packages/race/README.md).

Przycisk w `/promocje` resetuje wyłącznie `GRILL10` do jednego dostępnego użycia.
Endpoint resetu służy do lokalnej demonstracji.

## Podatność i poprawka

W wariancie `vulnerable` kod odczytuje `uses_left`, sprawdza wartość większą od
zera, a później aktualizuje i zatwierdza rekord. Wspólne opóźnienie 150 ms jest
celowym elementem demonstracji, nie warunkiem wystąpienia TOCTOU.

W wariancie `secure` jedno warunkowe `UPDATE coupons SET uses_left = uses_left - 1
WHERE code = :code AND uses_left > 0 RETURNING ...` rozstrzyga wyścig po stronie
PostgreSQL. Wiele procesów aplikacji korzysta z tej samej atomowej gwarancji.

## Demonstracja

Ustaw `BBQ_MODULE_RACE=vulnerable` w `.env`, uruchom ponownie API i wywołaj
`uv run python packages/race/tools/race_detector.py`. Następnie zmień flagę na `secure`, ponownie
uruchom API i użyj tego samego detektora. Detektor przed każdą serią resetuje
kupon bezpośrednio w PostgreSQL.

Opcjonalny klient Race The Web można uruchomić poleceniem
`race-the-web packages/race/tools/race-the-web.toml`. Generuje żądania i porównuje
odpowiedzi, ale semantyczną kontrolę limitu robi `packages/race/tools/race_detector.py`.

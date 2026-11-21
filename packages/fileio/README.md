# bbq-fileio: Arbitrary File Read/Write

Instrukcje produktów: `GET /api/storage?name=<plik>` (odczyt) i
`POST /api/storage?name=<plik>` (zapis). Pliki instrukcji (`manual-<id>.txt`)
leżą w katalogu dozwolonym; obok niego jest `secret.txt` — cel ataku.

Pełny scenariusz demonstracyjny: [docs/podatnosci/FileIO.md](../../docs/podatnosci/FileIO.md).

Wariant ustawiasz w `.env`:

```
BBQ_MODULE_FILEIO=vulnerable   # vulnerable | secure | off
```

## ❌ Wersja podatna ([vulnerable/repository.py](src/bbq_fileio/vulnerable/repository.py))

Nazwa pliku trafia wprost do ścieżki (`base / name`), bez sprawdzenia. Można
wyjść poza katalog instrukcji i czytać oraz zapisywać dowolne pliki:

- odczyt: `../secret.txt`, `/etc/passwd`, `/proc/self/environ` (zmienne środowiska),
- zapis: `../pwned.txt` tworzy plik poza katalogiem instrukcji.

## ✅ Wersja poprawiona ([secure/repository.py](src/bbq_fileio/secure/repository.py))

Ścieżka jest rozwijana (`Path.resolve()`) i sprawdzana: musi pozostać wewnątrz
katalogu instrukcji, inaczej odczyt i zapis są odrzucane (`../` i ścieżki
bezwzględne nie przechodzą).

## Testy

[tests/test_fileio_repositories.py](tests/test_fileio_repositories.py) uruchamia
te same scenariusze na obu wariantach: zwykły odczyt/zapis działa w obu, a
ucieczka poza katalog wycieka sekret w `vulnerable` i jest blokowana w `secure`.

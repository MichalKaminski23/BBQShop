# bbq-path-traversal: Path Traversal

Endpoint demonstracyjny: `GET /api/files/{ścieżka}`. Pliki graficzne (`jpg`,
`png`, `gif`, `webp` i `svg`) są zwracane bezpośrednio jako obrazy, więc
przeglądarka może je wyświetlić.

Wariant ustawiasz w `.env`:

```
BBQ_MODULE_PATH_TRAVERSAL=vulnerable   # vulnerable | secure | off
```

## Wersja podatna

Wariant podatny dokleja podaną ścieżkę do katalogu `public`, ale jej nie
normalizuje ani nie sprawdza. Sekwencja `..` pozwala wyjść poza ten katalog i
odczytać pliki aplikacji:

```
GET /api/files/../../README.md
```

odczytanie pliku win.ini ()

```
GET /api/files/../../../../../../../../../../Windows/win.ini
```

## Wersja poprawiona

Wariant bezpieczny normalizuje ścieżkę przez `Path.resolve()` i odrzuca ją,
jeśli wynik znajduje się poza katalogiem `public`. Próba odczytu pliku spoza
dozwolonego katalogu zwraca `400`.

Przykład prawidłowego żądania:

```
GET /api/files/menu.txt
```

Przykład obrazu:

```
GET /api/files/2384db1abef65abbd670acb234121106.jpg
```

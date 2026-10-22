# bbq-nosqli: NoSQL Injection

Logowanie: `POST /api/login` z ciałem `{"username": "...", "password": "..."}`.
Użytkownicy są w kolekcji MongoDB `users` (hasła są hashowane, PBKDF2).

Wariant ustawiasz w `.env`:

```
BBQ_MODULE_NOSQLI=vulnerable   # vulnerable | secure | off
```

## ❌ Wersja podatna ([vulnerable/repository.py](src/bbq_nosqli/vulnerable/repository.py))

Endpoint przyjmuje **surowy JSON** i wkleja wartości wprost do filtra zapytania Mongo:

```python
await users.find_one({"username": username})
```

Gdy `username`/`password` jest obiektem, staje się **operatorem zapytania**, a nie
napisem. Operator taki jak `{"$ne": null}` pasuje do dowolnego dokumentu, więc można
zalogować się bez znajomości loginu i hasła (pierwszym użytkownikiem jest `admin`).

**Przykładowy atak:**

```json
POST /api/login
{"username": {"$ne": null}, "password": {"$ne": null}}
```

W odpowiedzi dostajemy sesję administratora (`"role": "admin"`).

## ✅ Wersja poprawiona ([secure/repository.py](src/bbq_nosqli/secure/repository.py))

- Login i hasło muszą być **tekstem** – model Pydantic `LoginRequest` odrzuca
  obiekty (operatory) zwracając 422, a repozytorium dodatkowo sprawdza typ.
- Filtr zawiera tylko nazwę użytkownika; hasło jest weryfikowane osobno przez
  porównanie hashy w czasie stałym (`verify_password`), nigdy w filtrze zapytania.

## Testy

[tests/test_nosqli_repositories.py](tests/test_nosqli_repositories.py) uruchamia te same
scenariusze na obu wariantach:

- poprawne dane logują, błędne hasło jest odrzucane w obu wariantach,
- payload z operatorem `{"$ne": null}` loguje bez danych w `vulnerable`,
- ten sam payload w `secure` nie loguje nikogo.

[tests/test_nosqli_app.py](tests/test_nosqli_app.py) sprawdza to samo przez HTTP,
w tym odrzucenie operatorów przez walidację (422) w wariancie poprawionym.

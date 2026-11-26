# scripts

Skrypty pomocnicze do demonstracji i weryfikacji podatności BBQShop.

## Detektory (skan działającej aplikacji)

Odpytują **aktualnie uruchomione API** i próbują exploita. Jeśli moduł jest w trybie
`vulnerable`, atak przechodzi i skrypt zgłasza znalezisko; na `secure` nic nie wykrywa.
Są **nieniszczące** (tylko odczyt / próba logowania). Każdy działa też samodzielnie.

| Skrypt | Podatność | Endpoint |
|---|---|---|
| `scan-nosqli.ps1` | NoSQL Injection | `POST /api/login` (operator `{"$ne": null}`) |
| `scan-sqli.ps1`   | SQL Injection   | `GET /api/products/search` (UNION z `admin_secrets`) |
| `scan-fileio.ps1` | Arbitrary File Read | `GET /api/storage` (`../secret.txt`) |

Kod wyjścia każdego: `1` = wykryto, `0` = czysto, `2` = API nie odpowiada.

Wspólne funkcje HTTP są w `_scan-common.ps1` (dot-source, nie uruchamiać bezpośrednio).

## Runner

`scan-all.ps1` — odpala **wszystkie** `scan-*.ps1` z tego folderu i wypisuje zbiorcze
podsumowanie. Kod wyjścia: `1` = wykryto przynajmniej jedną, `0` = czysto, `2` = API down.

```powershell
# wszystkie naraz:
pwsh ./scripts/scan-all.ps1

# pojedyncza podatność:
pwsh ./scripts/scan-nosqli.ps1

# inny adres API:
pwsh ./scripts/scan-all.ps1 -BaseUrl http://localhost:8000
```

Wymaganie: działający stack (`docker compose up -d`, API na `localhost:8000`).

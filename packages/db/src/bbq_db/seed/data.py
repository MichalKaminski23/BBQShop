"""Dane przykładowe. Wszystkie hasła, klucze i sekrety są fikcyjne."""

from decimal import Decimal
from typing import Any

PRODUCTS: list[dict[str, Any]] = [
    {
        "name": "Grill węglowy Kettle 57 cm",
        "category": "Grille",
        "price": Decimal("899.00"),
        "stock": 12,
        "description": "Klasyczny grill kulisty z pokrywą i termometrem.",
    },
    {
        "name": "Grill gazowy Flame 3",
        "category": "Grille",
        "price": Decimal("2499.00"),
        "stock": 1,  # ostatnia sztuka – do demonstracji race condition
        "description": "Trzy palniki, boczna półka i ruszt żeliwny.",
    },
    {
        "name": "Węgiel drzewny dębowy 10 kg",
        "category": "Paliwo",
        "price": Decimal("69.99"),
        "stock": 80,
        "description": "Duże kawałki, długie i równe żarzenie.",
    },
    {
        "name": "Brykiet kokosowy 5 kg",
        "category": "Paliwo",
        "price": Decimal("49.99"),
        "stock": 45,
        "description": "Bez dymu i zapachu, idealny do długiego grillowania.",
    },
    {
        "name": "Szczypce do grilla 45 cm",
        "category": "Akcesoria",
        "price": Decimal("39.90"),
        "stock": 30,
        "description": "Stal nierdzewna, blokada zamykania.",
    },
    {
        "name": "Termometr do mięsa Bluetooth",
        "category": "Akcesoria",
        "price": Decimal("159.00"),
        "stock": 8,
        "description": "Dwie sondy i aplikacja na telefon.",
    },
    {
        "name": "Sos BBQ Smoky Hickory",
        "category": "Przyprawy",
        "price": Decimal("24.50"),
        "stock": 60,
        "description": "Słodko-dymny sos do żeberek.",
    },
]

SECRETS: list[dict[str, Any]] = [
    {"name": "admin_password", "value": "FLAG{sqli_union_select_works}"},
    {"name": "payment_api_key", "value": "sk_test_bbqshop_not_a_real_key"},
]

COUPONS: list[dict[str, Any]] = [
    # Kupon jednorazowy – do demonstracji race condition.
    {"code": "GRILL10", "discount_percent": 10, "uses_left": 1},
    {"code": "LATO2026", "discount_percent": 5, "uses_left": 100},
]

# Zamówienia: (klient, [(nazwa produktu, ilość), ...]) – do demonstracji N+1.
ORDERS: list[tuple[str, list[tuple[str, int]]]] = [
    ("Jan Kowalski", [("Grill węglowy Kettle 57 cm", 1), ("Węgiel drzewny dębowy 10 kg", 2)]),
    ("Anna Nowak", [("Brykiet kokosowy 5 kg", 3), ("Szczypce do grilla 45 cm", 1)]),
    ("Piotr Wiśniewski", [("Termometr do mięsa Bluetooth", 1), ("Sos BBQ Smoky Hickory", 4)]),
    ("Ewa Zielińska", [("Sos BBQ Smoky Hickory", 2)]),
]

# Użytkownicy MongoDB: (login, hasło, rola).
USERS: list[tuple[str, str, str]] = [
    ("admin", "Admin123!", "admin"),
    ("jan", "grill2026", "customer"),
    ("anna", "kielbaska", "customer"),
]

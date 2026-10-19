"""Dane przykładowe modułu SQLi (wstawiane tylko do pustych tabel)."""

from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_sqli.models import AdminSecret, Product

PRODUCTS: list[dict[str, object]] = [
    {
        "name": "Grill węglowy Kettle 57 cm",
        "category": "Grille",
        "price": Decimal("899.00"),
        "description": "Klasyczny grill kulisty z pokrywą i termometrem.",
    },
    {
        "name": "Grill gazowy Flame 3",
        "category": "Grille",
        "price": Decimal("2499.00"),
        "description": "Trzy palniki, boczna półka i ruszt żeliwny.",
    },
    {
        "name": "Węgiel drzewny dębowy 10 kg",
        "category": "Paliwo",
        "price": Decimal("69.99"),
        "description": "Duże kawałki, długie i równe żarzenie.",
    },
    {
        "name": "Brykiet kokosowy 5 kg",
        "category": "Paliwo",
        "price": Decimal("49.99"),
        "description": "Bez dymu i zapachu, idealny do długiego grillowania.",
    },
    {
        "name": "Szczypce do grilla 45 cm",
        "category": "Akcesoria",
        "price": Decimal("39.90"),
        "description": "Stal nierdzewna, blokada zamykania.",
    },
    {
        "name": "Termometr do mięsa Bluetooth",
        "category": "Akcesoria",
        "price": Decimal("159.00"),
        "description": "Dwie sondy i aplikacja na telefon.",
    },
    {
        "name": "Sos BBQ Smoky Hickory",
        "category": "Przyprawy",
        "price": Decimal("24.50"),
        "description": "Słodko-dymny sos do żeberek.",
    },
]

# Fikcyjne dane – mają tylko pokazać, co da się wyciągnąć przez SQLi.
SECRETS: list[dict[str, object]] = [
    {"name": "admin_password", "value": "FLAG{sqli_union_select_works}"},
    {"name": "payment_api_key", "value": "sk_test_bbqshop_not_a_real_key"},
]


async def seed(session: AsyncSession) -> None:
    if not await session.scalar(select(exists().select_from(Product))):
        session.add_all(Product(**data) for data in PRODUCTS)
    if not await session.scalar(select(exists().select_from(AdminSecret))):
        session.add_all(AdminSecret(**data) for data in SECRETS)
    await session.flush()

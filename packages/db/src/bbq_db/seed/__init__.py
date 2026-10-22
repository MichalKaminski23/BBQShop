"""Dane przykładowe sklepu (wstawiane tylko do pustych tabel i kolekcji)."""

from bbq_db.seed.seed import seed_mongo, seed_postgres

__all__ = ["seed_mongo", "seed_postgres"]

"""Wspólna baza modeli ORM."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Klasa bazowa wszystkich tabel PostgreSQL."""

"""Schematy żądań i odpowiedzi API modułu NoSQLi."""

from typing import Literal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Dane logowania wymuszone jako tekst (wariant poprawiony)."""

    username: str
    password: str


class LoginOut(BaseModel):
    """Wynik udanego logowania."""

    username: str
    role: Literal["customer", "admin"]

"""Schematy żądań i odpowiedzi modułu File I/O."""

from pydantic import BaseModel


class FileContent(BaseModel):
    """Odczytany plik."""

    name: str
    content: str


class WriteRequest(BaseModel):
    """Treść do zapisania."""

    content: str


class WriteResult(BaseModel):
    """Wynik zapisu."""

    name: str
    written: int

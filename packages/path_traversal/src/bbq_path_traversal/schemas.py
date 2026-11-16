"""Schematy odpowiedzi API modułu path traversal."""

from pydantic import BaseModel, ConfigDict


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    filename: str
    content: str

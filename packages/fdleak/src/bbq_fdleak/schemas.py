"""Schematy odpowiedzi modułu fdleak."""

from pydantic import BaseModel, Field


class ResourceDemoResult(BaseModel):
    resource_type: str
    opened_count: int = Field(ge=0)
    closed_count: int = Field(ge=0)

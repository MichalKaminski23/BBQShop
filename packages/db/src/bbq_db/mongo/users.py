"""Kolekcja ``users`` i hashowanie haseł (PBKDF2 z biblioteki standardowej)."""

import hashlib
import hmac
import secrets
from typing import Literal, TypedDict

USERS_COLLECTION = "users"

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 200_000


class UserDocument(TypedDict):
    username: str
    password_hash: str
    role: Literal["customer", "admin"]


def hash_password(password: str) -> str:
    """Zwraca hash w formacie ``pbkdf2_sha256$<iteracje>$<sól>$<hash>``."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS)
    return f"{_ALGORITHM}${_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Sprawdza hasło w czasie stałym."""
    algorithm, iterations, salt, expected = password_hash.split("$")
    if algorithm != _ALGORITHM:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)

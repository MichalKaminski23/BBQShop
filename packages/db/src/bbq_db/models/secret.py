from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from bbq_db.base import Base


class AdminSecret(Base):
    """Dane, których nie zwraca żaden endpoint – cel ataku SQLi."""

    __tablename__ = "admin_secrets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    value: Mapped[str] = mapped_column(String(200))

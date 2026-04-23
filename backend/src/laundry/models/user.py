"""User model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from laundry.db.database import Base

if TYPE_CHECKING:
    from laundry.models.session import CoinTransaction, LaundrySession


class User(Base):
    """User model representing a Telegram user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    block: Mapped[str] = mapped_column(String(1))
    coins: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sessions: Mapped[list["LaundrySession"]] = relationship(back_populates="user")
    transactions: Mapped[list["CoinTransaction"]] = relationship(back_populates="user")

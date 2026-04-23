"""Session and transaction models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from laundry.db.database import Base
from laundry.models.machine import Machine
from laundry.models.user import User


class LaundrySession(Base):
    """Laundry session representing a machine claim."""

    __tablename__ = "laundry_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    machine_id: Mapped[int] = mapped_column(Integer, ForeignKey("machines.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expected_end_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    done_notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="sessions")
    machine: Mapped["Machine"] = relationship(back_populates="sessions")


class CoinTransaction(Base):
    """Coin transaction log."""

    __tablename__ = "coin_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(50))  # claim, release, ping_sent, ping_received
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="transactions")

"""Powerup models for the gamification system."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from laundry.db.database import Base

if TYPE_CHECKING:
    from laundry.models.machine import Machine
    from laundry.models.user import User


class PowerupType(str, Enum):
    """
    Available powerup types.

    This is a Python Enum that also inherits from str, so:
    - PowerupType.SPAM_BOMB == "spam_bomb" (can compare to strings)
    - Can be used directly in JSON responses
    """
    SPAM_BOMB = "spam_bomb"
    NAME_SHAME = "name_shame"


class Powerup(Base):
    """
    Powerup definition - stores the "template" for each powerup type.

    This is like a product catalog - it defines WHAT powerups exist,
    not who owns them. Seeded once at startup.
    """

    __tablename__ = "powerups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), unique=True)  # PowerupType value
    name: Mapped[str] = mapped_column(String(100))  # Display name: "Spam Bomb"
    description: Mapped[str] = mapped_column(Text)  # Shown in shop UI
    cost: Mapped[int] = mapped_column(Integer)  # Price in coins
    icon: Mapped[str] = mapped_column(String(10))  # Emoji: "💣"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserPowerup(Base):
    """
    User's powerup inventory - tracks how many of each powerup a user owns.

    This is like a shopping cart that persists. When user buys a powerup,
    we either create a new row or increment the quantity.

    The UniqueConstraint ensures one row per user+powerup combination.
    """

    __tablename__ = "user_powerups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    powerup_id: Mapped[int] = mapped_column(Integer, ForeignKey("powerups.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - lets us do user_powerup.user or user_powerup.powerup
    user: Mapped["User"] = relationship(back_populates="powerups")
    powerup: Mapped["Powerup"] = relationship()

    # Composite unique constraint: only one row per user+powerup pair
    __table_args__ = (
        UniqueConstraint("user_id", "powerup_id", name="unique_user_powerup"),
    )


class SpamBombJob(Base):
    """
    Tracks active spam bomb jobs for delayed message sending.

    When someone uses a spam bomb, we don't send all 20 messages at once.
    Instead, we create a "job" and a scheduler sends batches over time.

    This is a simple "job queue" pattern - the scheduler polls this table
    every 15 seconds and processes incomplete jobs.
    """

    __tablename__ = "spam_bomb_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # Who sent it
    target_telegram_id: Mapped[int] = mapped_column(BigInteger)  # Who receives messages
    machine_id: Mapped[int] = mapped_column(Integer, ForeignKey("machines.id"))
    messages_sent: Mapped[int] = mapped_column(Integer, default=0)  # Progress counter
    messages_total: Mapped[int] = mapped_column(Integer, default=20)  # Target count
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # Set when done

    # Relationships for easy access to related data
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    machine: Mapped["Machine"] = relationship()

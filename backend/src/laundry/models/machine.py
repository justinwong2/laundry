"""Machine model."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from laundry.db.database import Base

if TYPE_CHECKING:
    from laundry.models.session import LaundrySession


class Machine(Base):
    """Machine model representing a washer or dryer."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10))  # e.g., "A1", "B2"
    type: Mapped[str] = mapped_column(String(10))  # "washer" or "dryer"
    block: Mapped[str] = mapped_column(String(1))  # A, B, C, D, E
    cycle_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    qr_code: Mapped[str] = mapped_column(String(50), unique=True)  # e.g., "E-WASHER-A1"

    sessions: Mapped[list["LaundrySession"]] = relationship(back_populates="machine")

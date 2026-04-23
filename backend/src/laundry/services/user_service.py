"""User service - business logic for user operations."""

from fastapi import HTTPException
from sqlalchemy import select

from laundry.config import settings
from laundry.db.database import async_session
from laundry.models.user import User


class UserService:
    """Service for user-related operations."""

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> dict | None:
        """Get user by Telegram ID."""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None

            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "block": user.block,
                "coins": user.coins,
                "created_at": user.created_at,
            }

    @staticmethod
    async def register(telegram_id: int, block: str, username: str | None = None) -> dict:
        """Register a new user."""
        if block not in ["A", "B", "C", "D", "E"]:
            raise HTTPException(status_code=400, detail="Invalid block")

        async with async_session() as session:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=400, detail="User already registered")

            user = User(
                telegram_id=telegram_id,
                username=username,
                block=block,
                coins=settings.coins_starting,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "block": user.block,
                "coins": user.coins,
                "created_at": user.created_at,
            }

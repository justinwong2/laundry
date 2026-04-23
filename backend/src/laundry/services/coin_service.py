"""Coin service - business logic for coin transactions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from laundry.db.database import async_session
from laundry.models.session import CoinTransaction
from laundry.models.user import User


class CoinService:
    """Service for coin-related operations."""

    @staticmethod
    async def add_coins(
        session: AsyncSession, user: User, amount: int, reason: str
    ) -> None:
        """Add or deduct coins from a user (within an existing session)."""
        user.coins += amount

        transaction = CoinTransaction(
            user_id=user.id,
            amount=amount,
            reason=reason,
        )
        session.add(transaction)

    @staticmethod
    async def get_transactions(telegram_id: int) -> list[dict]:
        """Get transaction history for a user."""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return []

            result = await session.execute(
                select(CoinTransaction)
                .where(CoinTransaction.user_id == user.id)
                .order_by(CoinTransaction.created_at.desc())
                .limit(50)
            )
            transactions = result.scalars().all()

            return [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "reason": t.reason,
                    "created_at": t.created_at,
                }
                for t in transactions
            ]

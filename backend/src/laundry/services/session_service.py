"""Session service - business logic for laundry sessions."""

from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select

from laundry.config import settings
from laundry.db.database import async_session
from laundry.models.machine import Machine
from laundry.models.session import LaundrySession
from laundry.models.user import User
from laundry.services.coin_service import CoinService


class SessionService:
    """Service for session-related operations."""

    @staticmethod
    async def claim(
        telegram_id: int, machine_id: int, message: str | None = None
    ) -> dict:
        """Claim a machine for a user."""
        async with async_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get machine
            result = await session.execute(
                select(Machine).where(Machine.id == machine_id)
            )
            machine = result.scalar_one_or_none()
            if not machine:
                raise HTTPException(status_code=404, detail="Machine not found")

            # Check if machine is already claimed
            result = await session.execute(
                select(LaundrySession).where(
                    LaundrySession.machine_id == machine_id,
                    LaundrySession.ended_at.is_(None),
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=400, detail="Machine is already in use")

            # Create session
            now = datetime.utcnow()
            laundry_session = LaundrySession(
                user_id=user.id,
                machine_id=machine_id,
                started_at=now,
                expected_end_at=now + timedelta(minutes=machine.cycle_duration_minutes),
                message=message,
            )
            session.add(laundry_session)

            # Award coins for claiming
            await CoinService.add_coins(
                session, user, settings.coins_claim, "claim"
            )

            await session.commit()
            await session.refresh(laundry_session)

            return {
                "id": laundry_session.id,
                "user_id": laundry_session.user_id,
                "machine_id": laundry_session.machine_id,
                "started_at": laundry_session.started_at,
                "expected_end_at": laundry_session.expected_end_at,
                "ended_at": laundry_session.ended_at,
                "message": laundry_session.message,
            }

    @staticmethod
    async def release(telegram_id: int, session_id: int) -> dict:
        """Release a machine."""
        async with async_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get session
            result = await session.execute(
                select(LaundrySession).where(LaundrySession.id == session_id)
            )
            laundry_session = result.scalar_one_or_none()
            if not laundry_session:
                raise HTTPException(status_code=404, detail="Session not found")

            if laundry_session.user_id != user.id:
                raise HTTPException(
                    status_code=403, detail="Cannot release another user's session"
                )

            if laundry_session.ended_at is not None:
                raise HTTPException(
                    status_code=400, detail="Session already released"
                )

            # Release
            laundry_session.ended_at = datetime.utcnow()

            # Award coins for releasing
            await CoinService.add_coins(
                session, user, settings.coins_release, "release"
            )

            await session.commit()

            return {
                "id": laundry_session.id,
                "user_id": laundry_session.user_id,
                "machine_id": laundry_session.machine_id,
                "started_at": laundry_session.started_at,
                "expected_end_at": laundry_session.expected_end_at,
                "ended_at": laundry_session.ended_at,
                "message": laundry_session.message,
            }

    @staticmethod
    async def get_active_for_user(telegram_id: int) -> list[dict]:
        """Get user's active sessions."""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return []

            result = await session.execute(
                select(LaundrySession).where(
                    LaundrySession.user_id == user.id,
                    LaundrySession.ended_at.is_(None),
                )
            )
            sessions = result.scalars().all()

            return [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "machine_id": s.machine_id,
                    "started_at": s.started_at,
                    "expected_end_at": s.expected_end_at,
                    "ended_at": s.ended_at,
                    "message": s.message,
                }
                for s in sessions
            ]

    @staticmethod
    async def ping(telegram_id: int, machine_id: int) -> dict:
        """Ping a machine's user."""
        async with async_session() as session:
            # Get pinger
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            pinger = result.scalar_one_or_none()
            if not pinger:
                raise HTTPException(status_code=404, detail="User not found")

            # Check coins
            if pinger.coins < settings.coins_ping_cost:
                raise HTTPException(
                    status_code=400, detail="Insufficient coins to ping"
                )

            # Get active session on machine
            result = await session.execute(
                select(LaundrySession)
                .where(
                    LaundrySession.machine_id == machine_id,
                    LaundrySession.ended_at.is_(None),
                )
            )
            laundry_session = result.scalar_one_or_none()
            if not laundry_session:
                raise HTTPException(
                    status_code=400, detail="No active session on this machine"
                )

            # Get owner
            result = await session.execute(
                select(User).where(User.id == laundry_session.user_id)
            )
            owner = result.scalar_one_or_none()
            if not owner:
                raise HTTPException(status_code=404, detail="Machine owner not found")

            if owner.id == pinger.id:
                raise HTTPException(
                    status_code=400, detail="Cannot ping your own machine"
                )

            # Deduct coins from pinger
            await CoinService.add_coins(
                session, pinger, -settings.coins_ping_cost, "ping_sent"
            )

            # Add coins to owner
            await CoinService.add_coins(
                session, owner, settings.coins_ping_receive, "ping_received"
            )

            await session.commit()

            # Send notification (fire and forget)
            from laundry.bot.notifications import (
                send_ping_notification,
                send_ping_received,
            )
            from laundry.models.machine import Machine

            result = await session.execute(
                select(Machine).where(Machine.id == machine_id)
            )
            machine = result.scalar_one()

            try:
                await send_ping_notification(
                    owner.telegram_id,
                    pinger.username or "Someone",
                    machine.code,
                    machine.type,
                )
                await send_ping_received(owner.telegram_id, settings.coins_ping_receive)
            except Exception:
                pass  # Don't fail the request if notification fails

            return {
                "success": True,
                "message": "Ping sent successfully",
                "new_balance": pinger.coins,
            }

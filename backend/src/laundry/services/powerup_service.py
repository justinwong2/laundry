"""Powerup service - business logic for buying and using powerups."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from laundry.config import settings
from laundry.db.database import async_session
from laundry.models.powerup import Powerup, PowerupType, SpamBombJob, UserPowerup
from laundry.models.session import LaundrySession
from laundry.models.user import User
from laundry.services.coin_service import CoinService


class PowerupService:
    """
    Service for powerup-related operations.

    Handles the full lifecycle:
    1. Listing available powerups (shop)
    2. Viewing user's inventory
    3. Buying powerups (deduct coins, add to inventory)
    4. Using powerups (validate, decrement inventory, trigger effect)
    """

    # ─────────────────────────────────────────────────────────────
    # SHOP & INVENTORY
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    async def get_all_powerups() -> list[dict]:
        """
        Get all available powerups for the shop.

        Returns a list of powerup definitions (not user-specific).
        """
        async with async_session() as session:
            result = await session.execute(select(Powerup))
            powerups = result.scalars().all()

            return [
                {
                    "id": p.id,
                    "type": p.type,
                    "name": p.name,
                    "description": p.description,
                    "cost": p.cost,
                    "icon": p.icon,
                }
                for p in powerups
            ]

    @staticmethod
    async def get_user_inventory(telegram_id: int) -> list[dict]:
        """
        Get a user's powerup inventory.

        Returns powerups the user owns with quantities > 0.
        Uses `selectinload` to eagerly load the related Powerup
        in the same query (avoids N+1 query problem).
        """
        async with async_session() as session:
            # First, find the user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return []

            # Get inventory items with quantity > 0, eagerly loading powerup details
            result = await session.execute(
                select(UserPowerup)
                .where(UserPowerup.user_id == user.id, UserPowerup.quantity > 0)
                .options(selectinload(UserPowerup.powerup))  # Eager load!
            )
            inventory = result.scalars().all()

            return [
                {
                    "id": up.id,
                    "powerup_id": up.powerup_id,
                    "powerup_type": up.powerup.type,
                    "powerup_name": up.powerup.name,
                    "powerup_icon": up.powerup.icon,
                    "quantity": up.quantity,
                }
                for up in inventory
            ]

    # ─────────────────────────────────────────────────────────────
    # BUYING POWERUPS
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    async def buy_powerup(telegram_id: int, powerup_type: str) -> dict:
        """
        Buy a powerup and add to user's inventory.

        Flow:
        1. Validate user exists
        2. Validate powerup type exists
        3. Check user has enough coins
        4. Deduct coins (creates transaction log)
        5. Add to inventory (create or increment)
        6. Commit and return result
        """
        async with async_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get powerup definition
            result = await session.execute(
                select(Powerup).where(Powerup.type == powerup_type)
            )
            powerup = result.scalar_one_or_none()
            if not powerup:
                raise HTTPException(status_code=404, detail="Powerup not found")

            # Check balance
            if user.coins < powerup.cost:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient coins. Need {powerup.cost}, "
                    f"have {user.coins}",
                )

            # Deduct coins (this also logs the transaction)
            await CoinService.add_coins(
                session, user, -powerup.cost, f"powerup_buy_{powerup_type}"
            )

            # Add to inventory (upsert pattern: find existing or create new)
            result = await session.execute(
                select(UserPowerup).where(
                    UserPowerup.user_id == user.id,
                    UserPowerup.powerup_id == powerup.id,
                )
            )
            user_powerup = result.scalar_one_or_none()

            if user_powerup:
                # Already have some - increment quantity
                user_powerup.quantity += 1
            else:
                # First purchase of this type - create new row
                user_powerup = UserPowerup(
                    user_id=user.id,
                    powerup_id=powerup.id,
                    quantity=1,
                )
                session.add(user_powerup)

            await session.commit()

            return {
                "success": True,
                "message": f"Purchased {powerup.name}!",
                "new_balance": user.coins,
                "quantity": user_powerup.quantity,
            }

    # ─────────────────────────────────────────────────────────────
    # USING POWERUPS
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    async def _validate_powerup_use(
        session: AsyncSession,
        telegram_id: int,
        powerup_type: PowerupType,
        machine_id: int,
    ) -> tuple[User, User, UserPowerup, LaundrySession]:
        """
        Common validation for using any powerup.

        Returns: (user, target, user_powerup, target_session)
        Raises HTTPException if any validation fails.

        This is a "helper method" prefixed with _ (private convention).
        It extracts shared logic to avoid code duplication.
        """
        # Get user
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get powerup definition
        result = await session.execute(
            select(Powerup).where(Powerup.type == powerup_type.value)
        )
        powerup = result.scalar_one_or_none()
        if not powerup:
            raise HTTPException(status_code=404, detail="Powerup not found")

        # Check user has this powerup in inventory
        result = await session.execute(
            select(UserPowerup).where(
                UserPowerup.user_id == user.id,
                UserPowerup.powerup_id == powerup.id,
                UserPowerup.quantity > 0,
            )
        )
        user_powerup = result.scalar_one_or_none()
        if not user_powerup:
            raise HTTPException(
                status_code=400, detail=f"No {powerup.name} in inventory"
            )

        # Get active session on the target machine
        result = await session.execute(
            select(LaundrySession).where(
                LaundrySession.machine_id == machine_id,
                LaundrySession.ended_at.is_(None),  # Active sessions only
            )
        )
        target_session = result.scalar_one_or_none()
        if not target_session:
            raise HTTPException(
                status_code=400, detail="No active session on this machine"
            )

        # Get target user
        result = await session.execute(
            select(User).where(User.id == target_session.user_id)
        )
        target = result.scalar_one_or_none()

        # Can't target yourself!
        if target.id == user.id:
            raise HTTPException(
                status_code=400, detail="Cannot use powerup on yourself"
            )

        return user, target, user_powerup, target_session

    @staticmethod
    async def use_spam_bomb(telegram_id: int, machine_id: int) -> dict:
        """
        Use a spam bomb powerup.

        Creates a SpamBombJob that the scheduler will process.
        The scheduler sends 5 messages every 15 seconds until 20 are sent.
        """
        async with async_session() as session:
            # Validate everything
            user, target, user_powerup, _ = await PowerupService._validate_powerup_use(
                session, telegram_id, PowerupType.SPAM_BOMB, machine_id
            )

            # Decrement inventory
            user_powerup.quantity -= 1

            # Create the spam bomb job for the scheduler to process
            job = SpamBombJob(
                user_id=user.id,
                target_telegram_id=target.telegram_id,
                machine_id=machine_id,
                messages_total=settings.powerup_spam_bomb_messages,
            )
            session.add(job)

            await session.commit()
            await session.refresh(job)  # Get the generated ID

            target_name = target.username or "User"
            msg_count = settings.powerup_spam_bomb_messages
            return {
                "success": True,
                "message": f"Spam bomb activated! {target_name} will receive "
                f"{msg_count} messages!",
                "job_id": job.id,
            }

    @staticmethod
    async def use_name_shame(telegram_id: int, machine_id: int) -> dict:
        """
        Use name and shame powerup.

        Immediately posts a message to the configured group chat.
        """
        # Check if group chat is configured
        if not settings.telegram_shame_group_id:
            raise HTTPException(
                status_code=500,
                detail="Shame group chat not configured. Contact admin.",
            )

        async with async_session() as session:
            # Validate everything
            validation = await PowerupService._validate_powerup_use(
                session, telegram_id, PowerupType.NAME_SHAME, machine_id
            )
            user, target, user_powerup, target_session = validation

            # Get machine info for the message
            from laundry.models.machine import Machine

            result = await session.execute(
                select(Machine).where(Machine.id == machine_id)
            )
            result.scalar_one()  # Verify machine exists

            # Decrement inventory
            user_powerup.quantity -= 1

            await session.commit()

            # Send the shame message (imported here to avoid circular imports)
            from laundry.bot.notifications import send_shame_message

            try:
                await send_shame_message(
                    target.username or "Anonymous",
                    target.block or "?",
                )
            except Exception as e:
                # Fire-and-forget pattern: log error but don't fail the request
                # The powerup was consumed, we don't refund on notification failure
                import logging

                logging.error(f"Failed to send shame message: {e}")
                return {
                    "success": True,
                    "message": "Powerup used but notification may have failed.",
                }

            target_name = target.username or "user"
            return {
                "success": True,
                "message": f"Posted shame message to group chat about {target_name}!",
            }

"""Reminder service - scheduled reminders for laundry sessions."""

from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from laundry.bot.notifications import send_done_notification, send_reminder
from laundry.config import settings
from laundry.db.database import async_session
from laundry.models.machine import Machine
from laundry.models.session import LaundrySession
from laundry.models.user import User

scheduler = AsyncIOScheduler()


async def check_reminders() -> None:
    """Check for sessions needing reminders."""
    now = datetime.utcnow()
    reminder_threshold = now + timedelta(minutes=settings.reminder_before_minutes)

    async with async_session() as session:
        # Sessions ending soon that haven't been reminded
        result = await session.execute(
            select(LaundrySession)
            .where(
                LaundrySession.ended_at.is_(None),
                LaundrySession.reminder_sent.is_(False),
                LaundrySession.expected_end_at <= reminder_threshold,
                LaundrySession.expected_end_at > now,
            )
        )
        sessions_to_remind = result.scalars().all()

        for laundry_session in sessions_to_remind:
            # Get user and machine
            user_result = await session.execute(
                select(User).where(User.id == laundry_session.user_id)
            )
            user = user_result.scalar_one_or_none()

            machine_result = await session.execute(
                select(Machine).where(Machine.id == laundry_session.machine_id)
            )
            machine = machine_result.scalar_one_or_none()

            if user and machine:
                try:
                    await send_reminder(user.telegram_id, machine.code, machine.type)
                    laundry_session.reminder_sent = True
                except Exception:
                    pass  # Log and continue

        await session.commit()


async def check_done_notifications() -> None:
    """Check for sessions that are done and need notification."""
    now = datetime.utcnow()

    async with async_session() as session:
        # Sessions that are past expected end but not yet released AND not yet notified
        result = await session.execute(
            select(LaundrySession)
            .where(
                LaundrySession.ended_at.is_(None),
                LaundrySession.expected_end_at <= now,
                LaundrySession.done_notification_sent.is_(False),
            )
        )
        done_sessions = result.scalars().all()

        for laundry_session in done_sessions:
            user_result = await session.execute(
                select(User).where(User.id == laundry_session.user_id)
            )
            user = user_result.scalar_one_or_none()

            machine_result = await session.execute(
                select(Machine).where(Machine.id == laundry_session.machine_id)
            )
            machine = machine_result.scalar_one_or_none()

            if user and machine:
                try:
                    await send_done_notification(
                        user.telegram_id, machine.code, machine.type
                    )
                    laundry_session.done_notification_sent = True
                except Exception:
                    pass  # Log and continue

        await session.commit()


def start_scheduler() -> None:
    """Start the reminder scheduler."""
    scheduler.add_job(check_reminders, "interval", minutes=1)
    scheduler.add_job(check_done_notifications, "interval", minutes=1)
    scheduler.start()


def stop_scheduler() -> None:
    """Stop the reminder scheduler."""
    scheduler.shutdown()

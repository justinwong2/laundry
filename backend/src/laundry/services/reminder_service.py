"""Reminder service - scheduled reminders for laundry sessions."""

from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from laundry.bot.notifications import (
    send_done_notification,
    send_reminder,
    send_spam_bomb_message,
)
from laundry.config import settings
from laundry.db.database import async_session
from laundry.models.machine import Machine
from laundry.models.powerup import SpamBombJob
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
            select(LaundrySession).where(
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
            select(LaundrySession).where(
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


async def process_spam_bombs() -> None:
    """
    Process active spam bomb jobs.

    This runs every 15 seconds. For each active job:
    1. Send a batch of messages (up to batch_size)
    2. Update the messages_sent counter
    3. Mark as completed when all messages sent

    This is a "job queue" pattern - work is queued in the database
    and processed incrementally by a background worker.
    """
    async with async_session() as session:
        # Get all incomplete spam bomb jobs
        result = await session.execute(
            select(SpamBombJob).where(SpamBombJob.completed_at.is_(None))
        )
        active_jobs = result.scalars().all()

        for job in active_jobs:
            # Calculate how many messages to send this batch
            remaining = job.messages_total - job.messages_sent
            batch_size = min(settings.powerup_spam_bomb_batch_size, remaining)

            # Get machine info for the message
            machine_result = await session.execute(
                select(Machine).where(Machine.id == job.machine_id)
            )
            machine = machine_result.scalar_one_or_none()

            # Get sender info
            user_result = await session.execute(
                select(User).where(User.id == job.user_id)
            )
            sender = user_result.scalar_one_or_none()

            # Send batch of messages
            for i in range(batch_size):
                try:
                    await send_spam_bomb_message(
                        job.target_telegram_id,
                        sender.username if sender else "Someone",
                        machine.code if machine else "Unknown",
                        machine.type if machine else "machine",
                        job.messages_sent + i + 1,  # Current message number
                        job.messages_total,
                    )
                except Exception:
                    pass  # Fire-and-forget: continue even if one message fails

            # Update progress
            job.messages_sent += batch_size

            # Mark complete if done
            if job.messages_sent >= job.messages_total:
                job.completed_at = datetime.utcnow()

        await session.commit()


def start_scheduler() -> None:
    """Start the reminder scheduler."""
    scheduler.add_job(check_reminders, "interval", minutes=1)
    scheduler.add_job(check_done_notifications, "interval", minutes=1)
    # Spam bomb runs every 15 seconds (sends 5 messages per batch = 20 msgs in 1 minute)
    scheduler.add_job(process_spam_bombs, "interval", seconds=15)
    scheduler.start()


def stop_scheduler() -> None:
    """Stop the reminder scheduler."""
    scheduler.shutdown()

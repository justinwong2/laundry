"""Service layer tests."""

import os

# Set test database URL BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from laundry.db.database import async_session, init_db
from laundry.models.machine import Machine
from laundry.models.session import LaundrySession
from laundry.models.user import User
from laundry.services.reminder_service import check_done_notifications


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Create database tables before each test."""
    await init_db()
    yield


class TestDoneNotificationSpam:
    """Tests for the done notification spam fix."""

    @pytest.mark.asyncio
    async def test_done_notification_sent_only_once(self):
        """
        When a session is done, notification should be sent exactly once.
        Running check_done_notifications() multiple times should NOT spam.
        """
        # Arrange: Create user, machine, and a "done" session
        async with async_session() as session:
            user = User(
                telegram_id=123456789,
                username="testuser",
                block="E",
                coins=10,
            )
            session.add(user)
            await session.flush()  # Get user.id

            machine = Machine(
                code="A1",
                type="washer",
                block="E",
                cycle_duration_minutes=45,
                qr_code="E-WASHER-A1",
            )
            session.add(machine)
            await session.flush()  # Get machine.id

            # Session that ended 10 minutes ago (done, needs notification)
            laundry_session = LaundrySession(
                user_id=user.id,
                machine_id=machine.id,
                started_at=datetime.utcnow() - timedelta(hours=1),
                expected_end_at=datetime.utcnow() - timedelta(minutes=10),
                ended_at=None,  # Not released yet
                reminder_sent=True,
                done_notification_sent=False,  # Not notified yet
            )
            session.add(laundry_session)
            await session.commit()

        # Act & Assert: Mock the notification sender and track calls
        with patch(
            "laundry.services.reminder_service.send_done_notification",
            new_callable=AsyncMock,
        ) as mock_send:
            # First check - should send notification
            await check_done_notifications()
            assert mock_send.call_count == 1, "First check should send notification"

            # Second check - should NOT send again (flag is now True)
            await check_done_notifications()
            assert mock_send.call_count == 1, "Second check should NOT send again"

            # Third check - still should not send
            await check_done_notifications()
            assert mock_send.call_count == 1, "Third check should NOT send again"

    @pytest.mark.asyncio
    async def test_done_notification_flag_is_set(self):
        """
        After sending done notification, the flag should be set to True.
        """
        # Arrange: Create user, machine, and a "done" session
        async with async_session() as session:
            user = User(
                telegram_id=987654321,
                username="flagtestuser",
                block="E",
                coins=10,
            )
            session.add(user)
            await session.flush()

            machine = Machine(
                code="B1",
                type="dryer",
                block="E",
                cycle_duration_minutes=60,
                qr_code="E-DRYER-B1",
            )
            session.add(machine)
            await session.flush()

            laundry_session = LaundrySession(
                user_id=user.id,
                machine_id=machine.id,
                started_at=datetime.utcnow() - timedelta(hours=1),
                expected_end_at=datetime.utcnow() - timedelta(minutes=5),
                ended_at=None,
                reminder_sent=True,
                done_notification_sent=False,
            )
            session.add(laundry_session)
            await session.commit()
            session_id = laundry_session.id

        # Act: Run the notification check
        with patch(
            "laundry.services.reminder_service.send_done_notification",
            new_callable=AsyncMock,
        ):
            await check_done_notifications()

        # Assert: Flag should now be True
        async with async_session() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(LaundrySession).where(LaundrySession.id == session_id)
            )
            updated_session = result.scalar_one()
            assert updated_session.done_notification_sent is True, "Flag should be True after notification"

    @pytest.mark.asyncio
    async def test_no_notification_for_released_session(self):
        """
        Sessions that have been released (ended_at is set) should NOT get notifications.
        """
        # Arrange: Create a released session
        async with async_session() as session:
            user = User(
                telegram_id=111222333,
                username="releaseduser",
                block="E",
                coins=10,
            )
            session.add(user)
            await session.flush()

            machine = Machine(
                code="C1",
                type="washer",
                block="E",
                cycle_duration_minutes=45,
                qr_code="E-WASHER-C1",
            )
            session.add(machine)
            await session.flush()

            # Session that is done AND released
            laundry_session = LaundrySession(
                user_id=user.id,
                machine_id=machine.id,
                started_at=datetime.utcnow() - timedelta(hours=1),
                expected_end_at=datetime.utcnow() - timedelta(minutes=10),
                ended_at=datetime.utcnow() - timedelta(minutes=5),  # Already released!
                reminder_sent=True,
                done_notification_sent=False,
            )
            session.add(laundry_session)
            await session.commit()

        # Act & Assert
        with patch(
            "laundry.services.reminder_service.send_done_notification",
            new_callable=AsyncMock,
        ) as mock_send:
            await check_done_notifications()
            assert mock_send.call_count == 0, "Released sessions should not get notifications"

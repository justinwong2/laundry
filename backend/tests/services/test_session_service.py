"""Tests for SessionService."""

from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from laundry.db.database import async_session
from laundry.models.session import LaundrySession
from laundry.models.user import User
from laundry.services.session_service import SessionService

# =============================================================================
# claim() tests
# =============================================================================


async def test_claim_success(test_user, test_machine):
    """User can claim an available machine and receive coins."""
    result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    assert result["machine_id"] == test_machine["id"]
    assert result["user_id"] == test_user["id"]
    assert result["ended_at"] is None
    assert result["expected_end_at"] is not None


async def test_claim_user_not_found(test_machine):
    """Claim fails with 404 if user doesn't exist."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.claim(
            telegram_id=99999,
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


async def test_claim_machine_not_found(test_user):
    """Claim fails with 404 if machine doesn't exist."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.claim(
            telegram_id=test_user["telegram_id"],
            machine_id=99999,
        )
    assert exc.value.status_code == 404
    assert "Machine not found" in exc.value.detail


async def test_claim_machine_already_in_use(test_user, second_user, test_machine):
    """Cannot claim a machine that's already in use."""
    # First user claims
    await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # Second user tries to claim same machine
    with pytest.raises(HTTPException) as exc:
        await SessionService.claim(
            telegram_id=second_user["telegram_id"],
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 400
    assert "already in use" in exc.value.detail


async def test_claim_with_duration_override(test_user, test_machine):
    """Custom duration override is respected."""
    result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
        cycle_duration_override=45,
    )

    # Check duration is ~45 minutes from start
    duration = result["expected_end_at"] - result["started_at"]
    assert duration == timedelta(minutes=45)


# =============================================================================
# release() tests
# =============================================================================


async def test_release_success(test_user, test_machine):
    """User can release their machine after timer expires."""
    # Claim first
    claim_result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # Manually set expected_end_at to past so we can release
    async with async_session() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(LaundrySession).where(LaundrySession.id == claim_result["id"])
        )
        laundry_session = result.scalar_one()
        laundry_session.expected_end_at = datetime.utcnow() - timedelta(minutes=1)
        await session.commit()

    # Now release
    release_result = await SessionService.release(
        telegram_id=test_user["telegram_id"],
        session_id=claim_result["id"],
    )

    assert release_result["ended_at"] is not None


async def test_release_user_not_found(test_user, test_machine):
    """Release fails with 404 if user doesn't exist."""
    claim_result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    with pytest.raises(HTTPException) as exc:
        await SessionService.release(
            telegram_id=99999,
            session_id=claim_result["id"],
        )
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


async def test_release_session_not_found(test_user):
    """Release fails with 404 if session doesn't exist."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.release(
            telegram_id=test_user["telegram_id"],
            session_id=99999,
        )
    assert exc.value.status_code == 404
    assert "Session not found" in exc.value.detail


async def test_release_wrong_user(test_user, second_user, test_machine):
    """Cannot release another user's session."""
    # First user claims
    claim_result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # Second user tries to release
    with pytest.raises(HTTPException) as exc:
        await SessionService.release(
            telegram_id=second_user["telegram_id"],
            session_id=claim_result["id"],
        )
    assert exc.value.status_code == 403
    assert "Cannot release another user's session" in exc.value.detail


async def test_release_before_finished(test_user, test_machine):
    """Cannot release machine before timer expires."""
    claim_result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    with pytest.raises(HTTPException) as exc:
        await SessionService.release(
            telegram_id=test_user["telegram_id"],
            session_id=claim_result["id"],
        )
    assert exc.value.status_code == 400
    assert "before it finishes" in exc.value.detail


# =============================================================================
# get_active_for_user() tests
# =============================================================================


async def test_get_active_returns_sessions(test_user, test_machine):
    """Returns user's active sessions."""
    await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    result = await SessionService.get_active_for_user(
        telegram_id=test_user["telegram_id"]
    )

    assert len(result) == 1
    assert result[0]["machine_id"] == test_machine["id"]


async def test_get_active_user_not_found():
    """Returns empty list for non-existent user."""
    result = await SessionService.get_active_for_user(telegram_id=99999)
    assert result == []


async def test_get_active_excludes_ended(test_user, test_machine):
    """Only returns sessions where ended_at is None."""
    # Claim and release
    claim_result = await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # Manually end the session
    async with async_session() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(LaundrySession).where(LaundrySession.id == claim_result["id"])
        )
        laundry_session = result.scalar_one()
        laundry_session.ended_at = datetime.utcnow()
        await session.commit()

    # Should return empty
    result = await SessionService.get_active_for_user(
        telegram_id=test_user["telegram_id"]
    )
    assert result == []


# =============================================================================
# ping() tests
# =============================================================================


async def test_ping_success(test_user, second_user, test_machine):
    """Pinger pays coins, owner receives coins."""
    # Second user claims machine
    await SessionService.claim(
        telegram_id=second_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # First user pings
    result = await SessionService.ping(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    assert result["success"] is True


async def test_ping_user_not_found(test_machine):
    """Ping fails with 404 if pinger doesn't exist."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.ping(
            telegram_id=99999,
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


async def test_ping_insufficient_coins(test_user, second_user, test_machine):
    """Ping fails if pinger doesn't have enough coins."""
    # Second user claims
    await SessionService.claim(
        telegram_id=second_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # Set first user's coins to 0
    async with async_session() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(User).where(User.telegram_id == test_user["telegram_id"])
        )
        user = result.scalar_one()
        user.coins = 0
        await session.commit()

    with pytest.raises(HTTPException) as exc:
        await SessionService.ping(
            telegram_id=test_user["telegram_id"],
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 400
    assert "Insufficient coins" in exc.value.detail


async def test_ping_no_active_session(test_user, test_machine):
    """Ping fails if no active session on machine."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.ping(
            telegram_id=test_user["telegram_id"],
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 400
    assert "No active session" in exc.value.detail


async def test_ping_own_machine(test_user, test_machine):
    """Cannot ping your own machine."""
    # User claims their own machine
    await SessionService.claim(
        telegram_id=test_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    with pytest.raises(HTTPException) as exc:
        await SessionService.ping(
            telegram_id=test_user["telegram_id"],
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 400
    assert "Cannot ping your own machine" in exc.value.detail


async def test_ping_owner_not_found(test_user, test_machine):
    """Ping fails if machine owner was deleted."""
    # Create a session with a non-existent user_id (simulating deleted owner)
    async with async_session() as session:
        laundry_session = LaundrySession(
            user_id=99999,  # Non-existent user
            machine_id=test_machine["id"],
            started_at=datetime.utcnow(),
            expected_end_at=datetime.utcnow() + timedelta(minutes=30),
        )
        session.add(laundry_session)
        await session.commit()

    with pytest.raises(HTTPException) as exc:
        await SessionService.ping(
            telegram_id=test_user["telegram_id"],
            machine_id=test_machine["id"],
        )
    assert exc.value.status_code == 404
    assert "owner not found" in exc.value.detail


# =============================================================================
# force_release() tests
# =============================================================================


async def test_force_release_success(test_user, second_user, test_machine):
    """Force release ends session and notifies owner."""
    # Second user claims
    await SessionService.claim(
        telegram_id=second_user["telegram_id"],
        machine_id=test_machine["id"],
    )

    # First user force releases
    result = await SessionService.force_release(
        telegram_id=test_user["telegram_id"],
        qr_code=test_machine["qr_code"],
    )

    assert result["success"] is True
    assert "released successfully" in result["message"]


async def test_force_release_user_not_found(test_machine):
    """Force release fails if releaser doesn't exist."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.force_release(
            telegram_id=99999,
            qr_code=test_machine["qr_code"],
        )
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


async def test_force_release_machine_not_found(test_user):
    """Force release fails if QR code invalid."""
    with pytest.raises(HTTPException) as exc:
        await SessionService.force_release(
            telegram_id=test_user["telegram_id"],
            qr_code="INVALID-QR-CODE",
        )
    assert exc.value.status_code == 404
    assert "Machine not found" in exc.value.detail


async def test_force_release_no_active_session(test_user, test_machine):
    """Force release returns success=False if no active session."""
    result = await SessionService.force_release(
        telegram_id=test_user["telegram_id"],
        qr_code=test_machine["qr_code"],
    )

    assert result["success"] is False
    assert "not currently in use" in result["message"]

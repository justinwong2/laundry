"""Test fixtures."""

import os

# Set test database URL BEFORE importing app (uses in-memory SQLite)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
# Set a dummy bot token for tests (notifications fail silently)
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token_12345"

import pytest
from httpx import ASGITransport, AsyncClient

from laundry.main import app
from laundry.db.database import Base, async_session, engine, init_db
from laundry.models.machine import Machine
from laundry.models.user import User


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Drop and recreate database tables before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user():
    """Create a test user with coins."""
    async with async_session() as session:
        user = User(
            telegram_id=12345,
            username="testuser",
            block="E",
            coins=100,
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
        }


@pytest.fixture
async def second_user():
    """Create a second test user for multi-user tests."""
    async with async_session() as session:
        user = User(
            telegram_id=67890,
            username="seconduser",
            block="E",
            coins=50,
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
        }


@pytest.fixture
async def test_machine():
    """Create a test machine in block E."""
    async with async_session() as session:
        machine = Machine(
            code="E1",
            type="washer",
            block="E",
            cycle_duration_minutes=30,
            qr_code="E-WASHER-E1",
        )
        session.add(machine)
        await session.commit()
        await session.refresh(machine)
        return {
            "id": machine.id,
            "code": machine.code,
            "type": machine.type,
            "block": machine.block,
            "cycle_duration_minutes": machine.cycle_duration_minutes,
            "qr_code": machine.qr_code,
        }

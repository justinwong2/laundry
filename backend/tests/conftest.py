"""Test fixtures."""

import os

# Set test database URL BEFORE importing app (uses in-memory SQLite)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
from httpx import ASGITransport, AsyncClient

from laundry.main import app
from laundry.db.database import init_db


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Create database tables before each test."""
    await init_db()
    yield


@pytest.fixture
async def client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

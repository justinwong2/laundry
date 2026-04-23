"""API endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from laundry.main import app
from laundry.config import settings


class TestDevAuthBypass:
    """Tests for the development authentication bypass."""

    @pytest.mark.asyncio
    async def test_dev_bypass_with_debug_enabled(self, monkeypatch):
        """
        When DEBUG=true and header is 'dev:{user_id}',
        the request should authenticate as that user.
        """
        # Arrange: Enable debug mode
        # Use object.__setattr__ to bypass Pydantic's immutability
        object.__setattr__(settings, "debug", True)

        # Act: Make request with dev auth header
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/users/me",
                headers={"X-Telegram-Init-Data": "dev:123456789"},
            )

        # Assert: Should not get 401 (authentication should pass)
        # Note: Might get 404 if user doesn't exist, but not 401
        assert response.status_code != 401, "Dev bypass should skip Telegram validation"

    @pytest.mark.asyncio
    async def test_dev_bypass_disabled_in_production(self, monkeypatch):
        """
        When DEBUG=false, the dev bypass should NOT work.
        """
        # Arrange: Disable debug mode
        object.__setattr__(settings, "debug", False)

        # Act: Try dev auth header
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/users/me",
                headers={"X-Telegram-Init-Data": "dev:123456789"},
            )

        # Assert: Should get 401 (authentication fails)
        assert response.status_code == 401, "Dev bypass should be disabled when DEBUG=false"

    @pytest.mark.asyncio
    async def test_dev_bypass_invalid_format(self, monkeypatch):
        """
        When debug=true but format is invalid, should still fail.
        """
        object.__setattr__(settings, "debug", True)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/users/me",
                headers={"X-Telegram-Init-Data": "invalid_format"},
            )

        assert response.status_code == 401, "Invalid dev format should fail authentication"

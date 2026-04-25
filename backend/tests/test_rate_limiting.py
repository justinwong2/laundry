"""Rate limiting tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from laundry.api.ratelimit import limiter
from laundry.config import settings
from laundry.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test."""
    limiter.reset()
    yield


class TestRateLimiting:
    """Tests for API rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_enforced_after_20_requests(self):
        """
        After 20 requests per minute, subsequent requests should return 429.
        """
        # Enable debug mode for easier testing (skip Telegram auth)
        object.__setattr__(settings, "debug", True)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Make 20 requests (should all succeed or return valid responses)
            for i in range(20):
                response = await client.get(
                    "/api/users/me",
                    headers={"X-Telegram-Init-Data": "dev:123456789"},
                )
                # Should not be rate limited yet (may be 404 if user not found)
                assert response.status_code != 429, (
                    f"Request {i+1} should not be rate limited"
                )

            # The 21st request should be rate limited
            response = await client.get(
                "/api/users/me",
                headers={"X-Telegram-Init-Data": "dev:123456789"},
            )
            assert response.status_code == 429, "21st request should be rate limited"

    @pytest.mark.asyncio
    async def test_rate_limit_response_includes_retry_after(self):
        """
        Rate limited responses should include Retry-After header.
        """
        object.__setattr__(settings, "debug", True)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Exhaust rate limit
            for _ in range(20):
                await client.get(
                    "/api/users/me",
                    headers={"X-Telegram-Init-Data": "dev:123456789"},
                )

            # Check rate limited response has proper headers
            response = await client.get(
                "/api/users/me",
                headers={"X-Telegram-Init-Data": "dev:123456789"},
            )

            assert response.status_code == 429
            has_retry_header = (
                "retry-after" in response.headers
                or "Retry-After" in response.headers
            )
            assert has_retry_header

    @pytest.mark.asyncio
    async def test_health_endpoint_not_rate_limited(self):
        """
        Health check endpoint should be exempt from rate limiting.
        """
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Make many requests to health endpoint
            for i in range(25):
                response = await client.get("/health")
                assert response.status_code == 200, (
                    f"Health check {i+1} should not be rate limited"
                )

"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse


def _get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.

    Uses X-Forwarded-For header if behind a proxy, otherwise falls back to
    the remote address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (client IP)
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter with 20 requests per minute default
limiter = Limiter(
    key_func=_get_client_identifier,
    default_limits=["20/minute"],
)


def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Handle rate limit exceeded errors with proper JSON response."""
    if "in " in exc.detail:
        retry_after = exc.detail.split("in ")[1].split(" ")[0]
    else:
        retry_after = "60"

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": retry_after,
        },
        headers={"Retry-After": retry_after},
    )

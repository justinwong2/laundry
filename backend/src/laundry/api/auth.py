"""Telegram WebApp authentication validation."""

import hashlib
import hmac
from urllib.parse import parse_qs

from fastapi import Depends, Header, HTTPException

from laundry.config import settings


def validate_init_data(init_data: str) -> dict:
    """
    Validate Telegram WebApp initData and extract user info.

    Args:
        init_data: The initData string from Telegram WebApp

    Returns:
        Parsed user data dict

    Raises:
        HTTPException: If validation fails
    """
    parsed = parse_qs(init_data)

    # Extract hash
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash in initData")

    # Build data check string
    data_check_arr = []
    for key, value in sorted(parsed.items()):
        if key != "hash":
            data_check_arr.append(f"{key}={value[0]}")
    data_check_string = "\n".join(data_check_arr)

    # Compute expected hash
    secret_key = hmac.new(
        b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256
    ).digest()
    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if received_hash != expected_hash:
        raise HTTPException(status_code=401, detail="Invalid initData signature")

    # Parse user JSON
    import json

    user_json = parsed.get("user", [None])[0]
    if not user_json:
        raise HTTPException(status_code=401, detail="Missing user in initData")

    return json.loads(user_json)


async def get_current_user_data(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
) -> dict:
    """Dependency to extract full current user data from initData header."""
    if settings.debug and x_telegram_init_data.startswith("dev:"):
        try:
            user_id = int(x_telegram_init_data.split(":")[1])
            return {"id": user_id, "username": f"dev_{user_id}", "first_name": "Dev", "last_name": "User"}
        except (IndexError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid dev auth format")
    
    return validate_init_data(x_telegram_init_data)


async def get_current_user_id(
    user_data: dict = Depends(get_current_user_data),
) -> int:
    """Dependency to extract just the Telegram user ID."""
    return user_data["id"]

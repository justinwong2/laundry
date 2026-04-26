"""Pydantic request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    """Request to register a new user."""

    block: str


class UserResponse(BaseModel):
    """User profile response."""

    id: int
    telegram_id: int
    username: str | None
    block: str
    coins: int
    created_at: datetime


class MachineResponse(BaseModel):
    """Machine details response."""

    id: int
    code: str
    type: str
    block: str
    cycle_duration_minutes: int
    qr_code: str
    current_session: "SessionResponse | None" = None


class SessionCreateRequest(BaseModel):
    """Request to claim a machine."""

    machine_id: int
    message: str | None = None
    cycle_duration_minutes: int | None = None


class SessionResponse(BaseModel):
    """Laundry session response."""

    id: int
    user_id: int
    machine_id: int
    started_at: datetime
    expected_end_at: datetime
    ended_at: datetime | None
    message: str | None
    username: str | None = None


class TransactionResponse(BaseModel):
    """Coin transaction response."""

    id: int
    amount: int
    reason: str
    created_at: datetime


class PingRequest(BaseModel):
    """Optional message for a ping."""

    message: str | None = None


class PingResponse(BaseModel):
    """Response after pinging a user."""

    success: bool
    message: str
    new_balance: int


class ForceReleaseResponse(BaseModel):
    """Response after force-releasing a machine."""

    success: bool
    message: str
    previous_owner_notified: bool


# ─────────────────────────────────────────────────────────────────────────────
# POWERUP SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────


class PowerupResponse(BaseModel):
    """
    Powerup definition for the shop.

    This is the "product listing" - shows what's available to buy.
    """

    id: int
    type: str  # "spam_bomb" or "name_shame"
    name: str  # "Spam Bomb"
    description: str  # Shown in shop UI
    cost: int  # Price in coins
    icon: str  # Emoji: "💣"


class UserPowerupResponse(BaseModel):
    """
    User's inventory item.

    Shows what the user owns and how many.
    """

    id: int
    powerup_id: int
    powerup_type: str
    powerup_name: str
    powerup_icon: str
    quantity: int


class BuyPowerupRequest(BaseModel):
    """Request to buy a powerup."""

    powerup_type: str  # "spam_bomb" or "name_shame"


class BuyPowerupResponse(BaseModel):
    """Response after buying a powerup."""

    success: bool
    message: str
    new_balance: int  # Updated coin balance
    quantity: int  # How many of this type user now has


class UsePowerupRequest(BaseModel):
    """Request to use a powerup on a machine."""

    machine_id: int  # Target machine with active session


class UsePowerupResponse(BaseModel):
    """Response after using a powerup."""

    success: bool
    message: str
    job_id: int | None = None  # Only for spam bomb (tracking ID)

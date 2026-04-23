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

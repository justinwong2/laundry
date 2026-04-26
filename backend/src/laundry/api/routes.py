"""REST API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from laundry.api.auth import get_current_user_data, get_current_user_id
from laundry.api.schemas import (
    ForceReleaseResponse,
    MachineResponse,
    PingRequest,
    PingResponse,
    SessionCreateRequest,
    SessionResponse,
    TransactionResponse,
    UserRegisterRequest,
    UserResponse,
)
from laundry.services.coin_service import CoinService
from laundry.services.machine_service import MachineService
from laundry.services.session_service import SessionService

router = APIRouter()


# Machines
@router.get("/machines", response_model=list[MachineResponse])
async def list_machines(telegram_id: int = Depends(get_current_user_id)):
    """List machines for the user's block."""
    from laundry.services.user_service import UserService

    user = await UserService.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await MachineService.get_all_with_status(block=user["block"])


@router.get("/machines/{machine_id}", response_model=MachineResponse)
async def get_machine(
    machine_id: int, telegram_id: int = Depends(get_current_user_id)
):
    """Get single machine details."""
    machine = await MachineService.get_by_id(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


# Sessions
@router.post("/sessions", response_model=SessionResponse)
async def claim_machine(
    request: SessionCreateRequest, telegram_id: int = Depends(get_current_user_id)
):
    """Claim a machine."""
    return await SessionService.claim(telegram_id, request.machine_id, request.message, request.cycle_duration_minutes)


@router.delete("/sessions/{session_id}", response_model=SessionResponse)
async def release_machine(
    session_id: int, telegram_id: int = Depends(get_current_user_id)
):
    """Release a machine."""
    return await SessionService.release(telegram_id, session_id)


@router.get("/sessions/mine", response_model=list[SessionResponse])
async def get_my_sessions(telegram_id: int = Depends(get_current_user_id)):
    """Get user's active sessions."""
    return await SessionService.get_active_for_user(telegram_id)


# Users
@router.get("/users/me", response_model=UserResponse)
async def get_current_user(telegram_id: int = Depends(get_current_user_id)):
    """Get current user profile + balance."""
    from laundry.services.user_service import UserService

    user = await UserService.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/register", response_model=UserResponse)
async def register_user(
    request: UserRegisterRequest, user_data: dict = Depends(get_current_user_data)
):
    """Register new user."""
    from laundry.services.user_service import UserService

    return await UserService.register(
        telegram_id=user_data["id"], 
        block=request.block,
        username=user_data.get("username")
    )


@router.get("/users/me/transactions", response_model=list[TransactionResponse])
async def get_my_transactions(telegram_id: int = Depends(get_current_user_id)):
    """Get coin transaction history."""
    return await CoinService.get_transactions(telegram_id)


# Interactions
@router.post("/ping/{machine_id}", response_model=PingResponse)
async def ping_machine_user(
    machine_id: int, request: PingRequest | None = None, telegram_id: int = Depends(get_current_user_id)
):
    """Ping a machine's user (costs coins)."""
    msg = request.message if request else None
    return await SessionService.ping(telegram_id, machine_id, msg)


@router.post("/machines/{qr_code}/force-release", response_model=ForceReleaseResponse)
async def force_release_machine(
    qr_code: str, telegram_id: int = Depends(get_current_user_id)
):
    """Force release a machine by QR code. Any authenticated user can do this."""
    return await SessionService.force_release(telegram_id, qr_code)

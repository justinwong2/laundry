"""REST API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from laundry.api.auth import get_current_user_data, get_current_user_id
from laundry.api.schemas import (
    BuyPowerupRequest,
    BuyPowerupResponse,
    ForceReleaseResponse,
    MachineResponse,
    PingRequest,
    PingResponse,
    PowerupResponse,
    SessionCreateRequest,
    SessionResponse,
    TransactionResponse,
    UsePowerupRequest,
    UsePowerupResponse,
    UserPowerupResponse,
    UserRegisterRequest,
    UserResponse,
)
from laundry.services.coin_service import CoinService
from laundry.services.machine_service import MachineService
from laundry.services.powerup_service import PowerupService
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
async def get_machine(machine_id: int, telegram_id: int = Depends(get_current_user_id)):
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
    return await SessionService.claim(
        telegram_id,
        request.machine_id,
        request.message,
        request.cycle_duration_minutes,
    )


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
        username=user_data.get("username"),
    )


@router.get("/users/me/transactions", response_model=list[TransactionResponse])
async def get_my_transactions(telegram_id: int = Depends(get_current_user_id)):
    """Get coin transaction history."""
    return await CoinService.get_transactions(telegram_id)


# Interactions
@router.post("/ping/{machine_id}", response_model=PingResponse)
async def ping_machine_user(
    machine_id: int,
    request: PingRequest | None = None,
    telegram_id: int = Depends(get_current_user_id),
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


# ─────────────────────────────────────────────────────────────────────────────
# POWERUPS
# These endpoints handle the powerup shop, inventory, and usage
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/powerups", response_model=list[PowerupResponse])
async def list_powerups(telegram_id: int = Depends(get_current_user_id)):
    """
    List all available powerups for the shop.

    Returns the "catalog" of powerups - what's available to buy.
    This is the same for all users (not personalized).
    """
    return await PowerupService.get_all_powerups()


@router.get("/powerups/inventory", response_model=list[UserPowerupResponse])
async def get_inventory(telegram_id: int = Depends(get_current_user_id)):
    """
    Get the current user's powerup inventory.

    Returns powerups the user owns with quantity > 0.
    """
    return await PowerupService.get_user_inventory(telegram_id)


@router.post("/powerups/buy", response_model=BuyPowerupResponse)
async def buy_powerup(
    request: BuyPowerupRequest, telegram_id: int = Depends(get_current_user_id)
):
    """
    Buy a powerup.

    Deducts coins from user's balance and adds the powerup to their inventory.
    If they already have some of this type, increments the quantity.
    """
    return await PowerupService.buy_powerup(telegram_id, request.powerup_type)


@router.post("/powerups/use/spam-bomb", response_model=UsePowerupResponse)
async def use_spam_bomb(
    request: UsePowerupRequest, telegram_id: int = Depends(get_current_user_id)
):
    """
    Use a spam bomb powerup on a machine.

    Requires:
    - User has at least 1 spam bomb in inventory
    - Target machine has an active session (someone's using it)
    - Target is not the user themselves

    Creates a background job that sends 20 messages over 1 minute.
    """
    return await PowerupService.use_spam_bomb(telegram_id, request.machine_id)


@router.post("/powerups/use/name-shame", response_model=UsePowerupResponse)
async def use_name_shame(
    request: UsePowerupRequest, telegram_id: int = Depends(get_current_user_id)
):
    """
    Use a name and shame powerup on a machine.

    Requires:
    - User has at least 1 name & shame in inventory
    - Target machine has an active session
    - Target is not the user themselves
    - TELEGRAM_SHAME_GROUP_ID is configured

    Immediately posts a message to the configured group chat.
    """
    return await PowerupService.use_name_shame(telegram_id, request.machine_id)

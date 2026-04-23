"""Send bot notifications (reminders, pings)."""

from telegram import Bot

from laundry.config import settings

bot = Bot(token=settings.telegram_bot_token)


async def send_reminder(telegram_id: int, machine_code: str, machine_type: str) -> None:
    """Send T-5min reminder notification."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"Your laundry in {machine_type.title()} {machine_code} is almost done!",
    )


async def send_done_notification(
    telegram_id: int, machine_code: str, machine_type: str
) -> None:
    """Send T-0 done notification."""
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"Your laundry in {machine_type.title()} {machine_code} is done! "
            "Please collect it."
        ),
    )


async def send_ping_notification(
    telegram_id: int,
    pinger_username: str,
    machine_code: str,
    machine_type: str,
) -> None:
    """Send ping notification to machine owner."""
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"@{pinger_username} is waiting for {machine_type.title()} {machine_code}. "
            "Please collect your laundry!"
        ),
    )


async def send_ping_received(telegram_id: int, amount: int) -> None:
    """Notify user they received coins from a ping."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"You received {amount} coin(s) as compensation for being pinged.",
    )

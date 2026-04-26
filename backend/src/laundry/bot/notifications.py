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
    custom_message: str | None = None,
) -> None:
    """Send ping notification to machine owner."""
    msg = f"@{pinger_username} is waiting for {machine_type.title()} {machine_code}."
    if custom_message:
        msg += f'\n\nThey say: "{custom_message}"'
    else:
        msg += " Please collect your laundry!"
        
    await bot.send_message(
        chat_id=telegram_id,
        text=msg,
    )


async def send_ping_received(telegram_id: int, amount: int) -> None:
    """Notify user they received coins from a ping."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"You received {amount} coin(s) as compensation for being pinged.",
    )


async def send_force_release_notification(
    telegram_id: int,
    releaser_username: str,
    machine_code: str,
    machine_type: str,
) -> None:
    """Notify original owner their session was force-released."""
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"Your session on {machine_type.title()} {machine_code} was force-released "
            f"by @{releaser_username}. Please collect your laundry if you haven't already."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# POWERUP NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────


async def send_spam_bomb_message(
    telegram_id: int,
    sender_username: str,
    machine_code: str,
    machine_type: str,
    message_num: int,
    total_messages: int,
) -> None:
    """
    Send a single spam bomb message.

    Called repeatedly by the scheduler (5 times per batch, 4 batches total).
    Uses varied message templates to make it more... impactful.
    """
    import random

    # Variety of messages to rotate through for maximum annoyance
    messages = [
        f"🚨 COLLECT YOUR LAUNDRY! ({message_num}/{total_messages})",
        f"📢 @{sender_username} is STILL waiting for {machine_type.title()} {machine_code}!",
        f"⚠️ YOUR LAUNDRY IS STILL THERE! Message {message_num} of {total_messages}",
        f"🔔 PING! PING! PING! Please collect from {machine_code}!",
        f"💣 SPAM BOMB {message_num}/{total_messages}: Go get your laundry!",
        f"⏰ Someone paid 20 coins to remind you... COLLECT YOUR LAUNDRY!",
        f"👀 @{sender_username} really wants {machine_type.title()} {machine_code}...",
    ]

    text = random.choice(messages)

    await bot.send_message(chat_id=telegram_id, text=text)


async def send_shame_message(
    target_username: str,
    machine_code: str,
    machine_type: str,
    shamer_username: str,
) -> None:
    """
    Post a name and shame message to the configured group chat.

    This is a PUBLIC message - sent to the group, not as a DM.
    The group ID comes from settings (environment variable).
    """
    text = (
        f"📢 **NAME AND SHAME** 📢\n\n"
        f"@{target_username} has been called out by @{shamer_username}!\n\n"
        f"Their laundry in {machine_type.title()} {machine_code} is done "
        f"but they haven't collected it yet.\n\n"
        f"Please be considerate and collect your laundry promptly! 🧺"
    )

    await bot.send_message(
        chat_id=settings.telegram_shame_group_id,
        text=text,
        parse_mode="Markdown",
    )

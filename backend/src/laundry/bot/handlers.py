"""Telegram bot command handlers."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

from laundry.config import settings


def _webapp_markup() -> InlineKeyboardMarkup | None:
    """Return Web App button markup if WEBAPP_URL is a valid HTTPS URL, else None."""
    if settings.webapp_url.startswith("https://"):
        keyboard = [
            [
                InlineKeyboardButton(
                    text="Open Laundry Room",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    return None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - register user and show Mini App button."""
    user = update.effective_user
    if not user:
        return

    reply_markup = _webapp_markup()
    suffix = "" if reply_markup else "\n\n(Mini App not yet deployed — stay tuned!)"

    await update.message.reply_text(
        f"Welcome to Laundry Bot, {user.first_name}!\n\n"
        "Track laundry machines, get reminders, and never miss your laundry again.\n\n"
        "Tap the button below to open the Laundry Room:" + suffix,
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show quick reference."""
    reply_markup = _webapp_markup()

    await update.message.reply_text(
        "Laundry Bot Help\n\n"
        "How it works:\n"
        "1. Scan QR on machine or tap a machine in the app\n"
        "2. Claim the machine to start your timer\n"
        "3. Get notified when your laundry is done\n"
        "4. Release the machine when you collect your laundry\n\n"
        "Earn coins by being a good neighbor!\n"
        "+1 coin: Claim a machine\n"
        "+2 coins: Release on time\n"
        "-3 coins: Ping someone to collect their laundry\n\n"
        "Tap below to get started:",
        reply_markup=reply_markup,
    )

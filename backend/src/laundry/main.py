"""Main application entry point - FastAPI app + bot startup."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram.ext import Application, CommandHandler

from laundry.api.routes import router
from laundry.bot.handlers import help_command, start_command
from laundry.config import settings
from laundry.db.database import init_db
from laundry.services.reminder_service import start_scheduler, stop_scheduler

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Store bot application globally so we can access it for shutdown
_bot_app: Application | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    Startup:
    1. Initialize database
    2. Start Telegram bot (if not in test mode)
    3. Start reminder scheduler

    Shutdown:
    1. Stop bot polling
    2. Stop scheduler
    """
    global _bot_app

    logger.info("Starting Laundry Bot API...")

    # 1. Initialize database
    await init_db()

    # 2. Start Telegram bot (skip in test mode - detected by in-memory DB)
    is_testing = ":memory:" in settings.database_url

    if not is_testing and settings.telegram_bot_token:
        logger.info("Starting Telegram bot...")
        _bot_app = Application.builder().token(settings.telegram_bot_token).build()

        # Register command handlers
        _bot_app.add_handler(CommandHandler("start", start_command))
        _bot_app.add_handler(CommandHandler("help", help_command))

        # Initialize and start (non-blocking)
        await _bot_app.initialize()
        await _bot_app.start()
        await _bot_app.updater.start_polling()
        logger.info("Telegram bot started!")
    else:
        logger.info("Skipping Telegram bot (test mode or no token)")

    # 3. Start reminder scheduler
    logger.info("Starting reminder scheduler...")
    start_scheduler()
    logger.info("Reminder scheduler started!")

    yield  # App is now running

    # --- Shutdown ---
    logger.info("Shutting down Laundry Bot API...")

    # Stop scheduler
    logger.info("Stopping reminder scheduler...")
    stop_scheduler()

    # Stop bot
    if _bot_app is not None:
        logger.info("Stopping Telegram bot...")
        await _bot_app.updater.stop()
        await _bot_app.stop()
        await _bot_app.shutdown()
        logger.info("Telegram bot stopped!")


app = FastAPI(
    title="Laundry Bot API",
    description="API for Telegram Mini App laundry room management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.webapp_url,
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

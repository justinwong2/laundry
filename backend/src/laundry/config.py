"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    telegram_bot_token: str
    database_url: str = "sqlite+aiosqlite:///laundry.db"
    log_level: str = "INFO"
    webapp_url: str = ""
    debug: bool = False  # Enable dev auth bypass (NEVER use in production!)

    # Coin settings
    coins_claim: int = 1
    coins_release: int = 2
    coins_ping_cost: int = 2  # Lowered from 3 to encourage engagement
    coins_ping_receive: int = 1
    coins_starting: int = 10

    # Reminder settings
    reminder_before_minutes: int = 5

    # Powerup settings
    powerup_spam_bomb_cost: int = 20
    powerup_spam_bomb_messages: int = 20  # Total messages to send
    powerup_spam_bomb_batch_size: int = 5  # Messages per batch (every 15 sec)
    powerup_name_shame_cost: int = 40
    telegram_shame_group_id: int | None = None  # Group chat ID for Name & Shame

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

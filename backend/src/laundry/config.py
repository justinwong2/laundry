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
    coins_ping_cost: int = 3
    coins_ping_receive: int = 1
    coins_starting: int = 10

    # Reminder settings
    reminder_before_minutes: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

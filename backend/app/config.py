from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str = "8586876585:AAHCnWNzopAY-xKsjcuJ_lvB6Y7UtD7txeo"
    WEBHOOK_SECRET: str = ""

    # FastAPI
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./hrbot.db"

    # HR Admin
    HR_TELEGRAM_IDS: str = ""

    # Bot Behavior
    REMINDER_INTERVAL_MINUTES: int = 1440
    MAX_REMINDER_ATTEMPTS: int = 3

    @property
    def hr_telegram_id_list(self) -> List[int]:
        """Parse HR Telegram IDs from comma-separated string."""
        if not self.HR_TELEGRAM_IDS:
            return []
        return [int(id.strip()) for id in self.HR_TELEGRAM_IDS.split(",") if id.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

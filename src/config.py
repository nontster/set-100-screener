import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Environment configuration manager."""

    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    LINE_CHANNEL_ACCESS_TOKEN: Optional[str] = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_USER_ID: Optional[str] = os.getenv("LINE_USER_ID")

    CACHE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
    CACHE_TTL_HOURS: int = 12

    @classmethod
    def validate_google_key(cls) -> str:
        """Validate that Google API key is configured."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is not set in environment variables or .env file."
            )
        return cls.GOOGLE_API_KEY

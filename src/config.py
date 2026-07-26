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

    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    VALID_MODELS = {
        "gemini-3.6-flash",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
    }

    CACHE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
    CACHE_TTL_HOURS: int = 12

    @classmethod
    def get_gemini_model(cls) -> str:
        """Return configured model or fallback to gemini-3.6-flash if invalid."""
        model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
        if model not in cls.VALID_MODELS:
            return "gemini-3.6-flash"
        return model

    @classmethod
    def validate_google_key(cls) -> str:
        """Validate that Google API key is configured."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is not set in environment variables or .env file."
            )
        return cls.GOOGLE_API_KEY

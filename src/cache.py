import os
import json
import time
from typing import Any, Dict, Optional
from src.config import Config


def _get_cache_filepath(ticker: str) -> str:
    """Get cache file path for a ticker."""
    cache_dir = Config.CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)
    sanitized_ticker = ticker.replace(".", "_").upper()
    return os.path.join(cache_dir, f"{sanitized_ticker}.json")


def get_cached_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached data for a ticker if it exists and is within 12-hour TTL.
    Returns None if cache is missing or expired.
    """
    filepath = _get_cache_filepath(ticker)
    if not os.path.exists(filepath):
        return None

    mtime = os.path.getmtime(filepath)
    ttl_seconds = Config.CACHE_TTL_HOURS * 3600

    if time.time() - mtime > ttl_seconds:
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def set_cached_data(ticker: str, data: Dict[str, Any]) -> None:
    """Save ticker data to JSON cache file."""
    filepath = _get_cache_filepath(ticker)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Failed to write cache for {ticker}: {e}")

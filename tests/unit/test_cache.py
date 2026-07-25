import os
import time
import pytest
from src.cache import get_cached_data, set_cached_data
from src.config import Config


def test_cache_miss_for_unknown_ticker(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "CACHE_DIR", str(tmp_path))
    assert get_cached_data("UNKNOWN_TICKER") is None


def test_cache_set_and_get_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "CACHE_DIR", str(tmp_path))
    sample_data = {"pe_ratio": 15.5, "roe": 18.2, "net_income": 5000000}

    set_cached_data("CPALL", sample_data)
    cached = get_cached_data("CPALL")

    assert cached is not None
    assert cached["pe_ratio"] == 15.5
    assert cached["roe"] == 18.2


def test_cache_expiration(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(Config, "CACHE_TTL_HOURS", 1)  # 1 hour TTL

    sample_data = {"pe_ratio": 12.0}
    set_cached_data("TEST_EXP", sample_data)

    filepath = os.path.join(tmp_path, "TEST_EXP.json")
    # Artificially set modification time to 2 hours ago
    past_mtime = time.time() - 7200
    os.utime(filepath, (past_mtime, past_mtime))

    assert get_cached_data("TEST_EXP") is None

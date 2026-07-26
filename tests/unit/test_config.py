import pytest
from src.config import Config


def test_get_gemini_model_default(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert Config.get_gemini_model() == "gemini-3.6-flash"


def test_get_gemini_model_valid(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.6-flash")
    assert Config.get_gemini_model() == "gemini-3.6-flash"


def test_get_gemini_model_invalid_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "invalid-model-name")
    assert Config.get_gemini_model() == "gemini-3.6-flash"

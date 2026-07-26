import os
import unittest
from unittest.mock import patch
from src.config import Config


class TestConfigLanguage(unittest.TestCase):
    """Test suite for ISO language code resolution and default fallback in Config."""

    def test_default_fallback_to_english_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(Config.get_app_language(), "en")

    def test_app_language_iso_thai(self):
        for val in ["th", "th_TH", "th-TH", "Thai", "TH"]:
            with patch.dict(os.environ, {"APP_LANGUAGE": val}, clear=True):
                self.assertEqual(
                    Config.get_app_language(),
                    "th",
                    f"Failed for APP_LANGUAGE={val}",
                )

    def test_app_language_iso_english(self):
        for val in ["en", "en_US", "en-US", "English", "EN"]:
            with patch.dict(os.environ, {"APP_LANGUAGE": val}, clear=True):
                self.assertEqual(
                    Config.get_app_language(),
                    "en",
                    f"Failed for APP_LANGUAGE={val}",
                )

    def test_summary_language_fallback_alias(self):
        with patch.dict(os.environ, {"SUMMARY_LANGUAGE": "Thai"}, clear=True):
            self.assertEqual(Config.get_app_language(), "th")

    def test_unsupported_language_fallback_to_english(self):
        with patch.dict(os.environ, {"APP_LANGUAGE": "invalid_lang_code"}, clear=True):
            self.assertEqual(Config.get_app_language(), "en")


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from unittest.mock import patch, MagicMock
from src.nodes.final_reporter import final_reporter_node


class TestFinalReporterLocalization(unittest.TestCase):
    """Test suite for final_reporter_node language localization & prompt instructions."""

    @patch("src.nodes.final_reporter.ChatGoogleGenerativeAI")
    @patch("src.nodes.final_reporter.Config")
    def test_final_reporter_thai_language_prompt(self, mock_config, mock_llm_cls):
        mock_config.GOOGLE_API_KEY = "dummy_key"
        mock_config.get_gemini_model.return_value = "gemini-3.6-flash"
        mock_config.get_app_language.return_value = "th"

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "รายงานสรุปสำหรับบริษัท EA: ให้คำแนะนำ **REJECT**"
        mock_llm.invoke.return_value = mock_response
        mock_llm_cls.return_value = mock_llm

        state = {
            "ticker": "EA.BK",
            "fraud_report": {"fraud_risk_level": "HIGH", "red_flags": ["Accounting Red Flag"]},
            "value_report": {"score": 45.0, "valuation_status": "Fair"},
            "sentiment_report": {"sentiment_score": 10.0, "overall_sentiment": "Positive"},
            "raw_data": {"company_name": "Energy Absolute"},
        }

        result = final_reporter_node(state)

        # Check LLM invoke prompt contains Thai instruction
        mock_llm.invoke.assert_called_once()
        invoked_prompt = mock_llm.invoke.call_args[0][0]
        self.assertIn("Thai", invoked_prompt)
        self.assertEqual(result["final_decision"]["recommendation"], "REJECT")
        self.assertIn("**REJECT**", result["final_decision"]["executive_summary"])

    @patch("src.nodes.final_reporter.ChatGoogleGenerativeAI")
    @patch("src.nodes.final_reporter.Config")
    def test_final_reporter_english_language_prompt(self, mock_config, mock_llm_cls):
        mock_config.GOOGLE_API_KEY = "dummy_key"
        mock_config.get_gemini_model.return_value = "gemini-3.6-flash"
        mock_config.get_app_language.return_value = "en"

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Analysis report for Energy Absolute: Recommendation is **REJECT**"
        mock_llm.invoke.return_value = mock_response
        mock_llm_cls.return_value = mock_llm

        state = {
            "ticker": "EA.BK",
            "fraud_report": {"fraud_risk_level": "HIGH"},
            "value_report": {"score": 45.0},
            "sentiment_report": {"sentiment_score": 10.0},
            "raw_data": {"company_name": "Energy Absolute"},
        }

        result = final_reporter_node(state)

        invoked_prompt = mock_llm.invoke.call_args[0][0]
        self.assertIn("English", invoked_prompt)
        self.assertIn("**REJECT**", result["final_decision"]["executive_summary"])


if __name__ == "__main__":
    unittest.main()

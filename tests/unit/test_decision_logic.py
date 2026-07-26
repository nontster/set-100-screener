import pytest
from src.nodes.final_reporter import final_reporter_node
from src.state import StockState


def test_high_fraud_risk_mandatory_reject_override():
    """Rule 1: Any stock with HIGH fraud risk MUST be categorized as REJECT regardless of valuation."""
    state: StockState = {
        "ticker": "HIGH_FRAUD_TICKER",
        "fraud_report": {
            "fraud_risk_level": "HIGH",
            "red_flags": ["Operating Cash Flow vs Net Income severe divergence"],
        },
        "value_report": {"score": 95, "valuation_status": "UNDERVALUED"},  # Extremely cheap valuation
        "sentiment_report": {"sentiment_score": 80},  # Positive sentiment
    }

    result = final_reporter_node(state)
    decision = result["final_decision"]

    # MUST be REJECT despite score 95
    assert decision["recommendation"] == "REJECT"


def test_severe_negative_news_sentiment_override():
    """Rule 2: Sentiment score < -50 overrides potential PASS."""
    state: StockState = {
        "ticker": "BAD_NEWS_TICKER",
        "fraud_report": {"fraud_risk_level": "LOW", "red_flags": []},
        "value_report": {"score": 85},
        "sentiment_report": {"sentiment_score": -60},  # Severe news risk
    }

    result = final_reporter_node(state)
    decision = result["final_decision"]

    # Must NOT be PASS
    assert decision["recommendation"] in ["WATCHLIST", "REJECT"]


def test_pass_recommendation_criteria():
    """Rule 3: LOW fraud risk + Value Score >= 70 + Sentiment Score >= -20 -> PASS."""
    state: StockState = {
        "ticker": "GOOD_TICKER",
        "fraud_report": {"fraud_risk_level": "LOW", "red_flags": []},
        "value_report": {"score": 75},
        "sentiment_report": {"sentiment_score": 10},
    }

    result = final_reporter_node(state)
    decision = result["final_decision"]

    assert decision["recommendation"] == "PASS"


def test_final_reporter_handles_list_response_content(monkeypatch):
    """Test that final_reporter_node safely handles AIMessage response with list content."""
    from src.config import Config

    class MockAIMessage:
        content = ["Executive summary text part 1. ", "Executive summary text part 2."]

    class MockLLM:
        def invoke(self, prompt):
            return MockAIMessage()

    monkeypatch.setattr(Config, "GOOGLE_API_KEY", "mock_key")
    monkeypatch.setattr(
        "src.nodes.final_reporter.ChatGoogleGenerativeAI",
        lambda **kwargs: MockLLM(),
    )

    state: StockState = {
        "ticker": "TEST_TICKER",
        "fraud_report": {"fraud_risk_level": "LOW", "red_flags": []},
        "value_report": {"score": 80},
        "sentiment_report": {"sentiment_score": 50},
    }

    result = final_reporter_node(state)
    decision = result["final_decision"]

    assert decision["executive_summary"] == "Executive summary text part 1. Executive summary text part 2."


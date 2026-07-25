import pytest
from src.nodes.final_reporter import final_reporter_node
from src.state import StockState


def test_total_score_calculation_low_fraud_risk():
    state: StockState = {
        "ticker": "CPALL",
        "fraud_report": {"fraud_risk_level": "LOW", "red_flags": []},
        "value_report": {"score": 80},
        "sentiment_report": {"sentiment_score": 50},
    }

    result = final_reporter_node(state)
    decision = result["final_decision"]

    # Value Score: 80 * 0.7 = 56.0
    # Normalized Sentiment: (50 + 100) / 2 = 75.0 -> 75.0 * 0.3 = 22.5
    # Total Score: 56.0 + 22.5 - 0 = 78.5
    assert decision["total_score"] == 78.5
    assert decision["recommendation"] == "PASS"


def test_total_score_calculation_medium_fraud_risk_penalty():
    state: StockState = {
        "ticker": "TEST",
        "fraud_report": {"fraud_risk_level": "MEDIUM", "red_flags": ["High D/E"]},
        "value_report": {"score": 80},
        "sentiment_report": {"sentiment_score": 50},
    }

    result = final_reporter_node(state)
    decision = result["final_decision"]

    # Raw score = 78.5 - 20.0 (penalty) = 58.5
    assert decision["total_score"] == 58.5
    assert decision["recommendation"] == "WATCHLIST"

from src.nodes.notification import (
    format_single_stock_telegram,
    format_batch_digest_telegram,
    notification_node,
)


def test_format_single_stock_telegram():
    result = {
        "ticker": "CPALL",
        "total_score": 78.5,
        "value_score": 80,
        "fraud_risk_level": "LOW",
        "sentiment_score": 50,
        "overall_sentiment": "POSITIVE",
        "executive_summary": "Solid value company.",
    }

    text = format_single_stock_telegram(result)
    assert "*PASS: CPALL*" in text
    assert "*Total Score*: 78.5/100" in text
    assert "*Fraud Risk*: LOW" in text


def test_format_batch_digest_telegram():
    results = [
        {"ticker": "CPALL", "recommendation": "PASS", "total_score": 82.0, "value_score": 85},
        {"ticker": "PTT", "recommendation": "WATCHLIST", "total_score": 65.0, "value_score": 70},
        {"ticker": "HIGH_RISK", "recommendation": "REJECT", "total_score": 30.0, "value_score": 90},
    ]

    text = format_batch_digest_telegram(results, "2026-07-25")
    assert "CPALL" in text
    assert "1 PASS | 1 WATCHLIST | 1 REJECT" in text


def test_notification_node_skips_watchlist(monkeypatch):
    state = {
        "ticker": "PTT",
        "final_decision": {"recommendation": "WATCHLIST", "total_score": 65.0},
    }

    result = notification_node(state)
    assert result["notification_sent"] is False

import pytest
from src.graph import run_single_stock_screening


def test_single_stock_screening_workflow_mock():
    """Integration test verifying full LangGraph workflow execution end-to-end."""
    result = run_single_stock_screening("CPALL")

    assert result["ticker"] == "CPALL"
    assert result["recommendation"] in ["PASS", "WATCHLIST", "REJECT"]
    assert 0.0 <= result["total_score"] <= 100.0
    assert result["fraud_risk_level"] in ["LOW", "MEDIUM", "HIGH", "N/A"]
    assert isinstance(result["executive_summary"], str)
    assert len(result["executive_summary"]) > 0

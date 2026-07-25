import pytest
from src.graph import run_single_stock_screening


def test_full_classification_pipeline_integration():
    """Integration test verifying that stock classification runs end-to-end in the graph."""
    result = run_single_stock_screening("ADVANC")

    assert result["ticker"] == "ADVANC"
    assert "classification_report" in result

    report = result["classification_report"]
    assert report is not None
    assert report["category"] in ["DIVIDEND", "GROWTH", "HYBRID", "NEUTRAL", "REJECTED"]
    assert report["payout_safety"] in ["SAFE", "CAUTION", "UNSAFE", "NOT_APPLICABLE"]
    assert isinstance(report["mega_trends"], list)
    assert isinstance(report["rationale"], str)
    assert len(report["rationale"]) > 0
    assert "metrics" in report

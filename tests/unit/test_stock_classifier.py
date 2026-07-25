import pytest
from src.nodes.stock_classifier import (
    calculate_quantitative_metrics,
    evaluate_mega_trends,
    calculate_classification_scores,
    stock_classifier_node,
)


def test_calculate_quantitative_metrics():
    raw_data = {
        "dividend_yield": 5.4,
        "pe_ratio": 12.0,
        "rev_cagr_3yr": 8.5,
        "eps_cagr_3yr": 10.0,
        "roe": 16.5,
    }
    metrics = calculate_quantitative_metrics(raw_data)
    assert metrics["dividend_yield"] == 5.4
    assert metrics["roe"] == 16.5
    # Payout ratio estimated from yield * PE = 5.4 * 12.0 = 64.8%
    assert metrics["payout_ratio"] == 64.8


def test_evaluate_mega_trends_ai_data_center():
    raw_data = {
        "company_name": "Advanced Data Center Utilities",
        "sector": "Technology & Utilities",
        "industry": "Data Center Infrastructure",
    }
    news_articles = [
        {"title": "Company expands AI Data Center power supply contract", "snippet": "Leading AI cloud data center provider"}
    ]
    res = evaluate_mega_trends(raw_data, news_articles)
    assert "AI & Data Center Infrastructure" in res["mega_trends"]
    assert res["mega_trend_score"] >= 50


def test_classification_scores_dividend_stock():
    metrics = {
        "dividend_yield": 5.5,
        "payout_ratio": 60.0,
        "rev_cagr_3yr": 2.0,
        "eps_cagr_3yr": 3.0,
        "roe": 12.0,
    }
    mega_trend_data = {"mega_trends": [], "mega_trend_score": 0}
    scores = calculate_classification_scores(metrics, mega_trend_data, fraud_risk_level="LOW")

    assert scores["category"] == "DIVIDEND"
    assert scores["payout_safety"] == "SAFE"
    assert scores["dividend_score"] >= 70


def test_classification_scores_growth_stock():
    metrics = {
        "dividend_yield": 1.2,
        "payout_ratio": 20.0,
        "rev_cagr_3yr": 16.0,
        "eps_cagr_3yr": 18.0,
        "roe": 18.0,
    }
    mega_trend_data = {"mega_trends": ["AI & Data Center Infrastructure"], "mega_trend_score": 50}
    scores = calculate_classification_scores(metrics, mega_trend_data, fraud_risk_level="LOW")

    assert scores["category"] == "GROWTH"
    assert scores["growth_score"] >= 70


def test_classification_scores_hybrid_stock():
    metrics = {
        "dividend_yield": 4.5,
        "payout_ratio": 65.0,
        "rev_cagr_3yr": 15.0,
        "eps_cagr_3yr": 16.0,
        "roe": 17.0,
    }
    mega_trend_data = {"mega_trends": ["AI & Data Center Infrastructure"], "mega_trend_score": 50}
    scores = calculate_classification_scores(metrics, mega_trend_data, fraud_risk_level="LOW")

    assert scores["category"] == "HYBRID"
    assert scores["dividend_score"] >= 70
    assert scores["growth_score"] >= 70


def test_safety_fraud_override_gate():
    metrics = {
        "dividend_yield": 8.0,
        "payout_ratio": 50.0,
        "rev_cagr_3yr": 20.0,
        "eps_cagr_3yr": 25.0,
        "roe": 22.0,
    }
    mega_trend_data = {"mega_trends": ["AI & Data Center Infrastructure"], "mega_trend_score": 75}

    # High accounting risk -> FORCED REJECTED
    scores = calculate_classification_scores(metrics, mega_trend_data, fraud_risk_level="HIGH")

    assert scores["category"] == "REJECTED"
    assert scores["dividend_score"] == 0
    assert scores["growth_score"] == 0
    assert scores["payout_safety"] == "UNSAFE"
    assert "FORCED OVERRIDE" in scores["rationale"]


def test_stock_classifier_node_execution():
    state = {
        "ticker": "TEST.BK",
        "raw_data": {
            "dividend_yield": 4.8,
            "pe_ratio": 14.0,
            "company_name": "Test Telecom Data Center",
            "sector": "Technology",
            "industry": "Data Center",
            "roe": 15.0,
        },
        "fraud_report": {"fraud_risk_level": "LOW"},
    }
    result = stock_classifier_node(state)
    assert "classification_report" in result
    report = result["classification_report"]
    assert report["ticker"] == "TEST.BK"
    assert report["category"] in ["DIVIDEND", "GROWTH", "HYBRID", "NEUTRAL"]
    assert "metrics" in report

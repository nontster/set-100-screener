import pytest
from pydantic import ValidationError
from src.schemas import (
    FraudAnalysisSchema,
    ValueAnalysisSchema,
    SentimentAnalysisSchema,
    FinalDecisionSchema,
)


def test_fraud_analysis_schema_valid():
    fraud = FraudAnalysisSchema(
        fraud_risk_level="LOW",
        cash_flow_quality="Operating cash flow aligns with net income.",
        red_flags=[],
        reasoning="Healthy accounting indicators.",
    )
    assert fraud.fraud_risk_level == "LOW"
    assert fraud.red_flags == []


def test_fraud_analysis_schema_invalid_risk_level():
    with pytest.raises(ValidationError):
        FraudAnalysisSchema(
            fraud_risk_level="VERY_HIGH",  # Invalid enum
            cash_flow_quality="Good",
            red_flags=[],
            reasoning="Test",
        )


def test_value_analysis_schema_valid():
    val = ValueAnalysisSchema(
        is_value_stock=True,
        score=85,
        valuation_status="UNDERVALUED",
        key_strengths=["ROE > 15%"],
        key_weaknesses=[],
    )
    assert val.score == 85
    assert val.is_value_stock is True


def test_value_analysis_schema_out_of_bounds_score():
    with pytest.raises(ValidationError):
        ValueAnalysisSchema(
            is_value_stock=True,
            score=150,  # Must be <= 100
            valuation_status="UNDERVALUED",
            key_strengths=[],
            key_weaknesses=[],
        )


def test_sentiment_analysis_schema_valid():
    sent = SentimentAnalysisSchema(
        overall_sentiment="POSITIVE",
        sentiment_score=45,
        key_catalysts=["New retail expansion"],
        key_risks=[],
        news_summary="Positive outlook for retail sector.",
    )
    assert sent.sentiment_score == 45


def test_sentiment_analysis_schema_out_of_bounds_score():
    with pytest.raises(ValidationError):
        SentimentAnalysisSchema(
            overall_sentiment="NEGATIVE",
            sentiment_score=-120,  # Must be >= -100
            key_catalysts=[],
            key_risks=[],
            news_summary="Test",
        )


def test_final_decision_schema_valid():
    decision = FinalDecisionSchema(
        recommendation="PASS",
        total_score=78.5,
        executive_summary="Solid value stock with low fraud risk.",
    )
    assert decision.recommendation == "PASS"
    assert decision.total_score == 78.5

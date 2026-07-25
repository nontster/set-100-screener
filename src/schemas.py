from typing import List, Literal
from pydantic import BaseModel, Field


class FraudAnalysisSchema(BaseModel):
    """Forensic accounting audit output schema."""

    fraud_risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Accounting risk assessment level: LOW, MEDIUM, or HIGH"
    )
    cash_flow_quality: str = Field(
        description="Assessment of Operating Cash Flow vs Net Income alignment and cash generation sustainability"
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="List of specific accounting anomalies or red flags detected",
    )
    reasoning: str = Field(
        description="Detailed explanation of the risk classification"
    )


class ValueAnalysisSchema(BaseModel):
    """Value & profitability screener output schema."""

    is_value_stock: bool = Field(
        description="True if stock meets fundamental value & quality parameters"
    )
    score: int = Field(
        ge=0,
        le=100,
        description="Valuation quality score from 0 to 100",
    )
    valuation_status: Literal["UNDERVALUED", "FAIRLY_VALUED", "OVERVALUED"] = Field(
        description="Valuation status relative to sector and historical metrics"
    )
    key_strengths: List[str] = Field(
        default_factory=list,
        description="Key financial strengths (e.g. ROE > 15%, positive FCF)",
    )
    key_weaknesses: List[str] = Field(
        default_factory=list,
        description="Key financial weaknesses or valuation concerns",
    )


class SentimentAnalysisSchema(BaseModel):
    """News sentiment analysis output schema."""

    overall_sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE"] = Field(
        description="Aggregate sentiment orientation from recent Thai financial news"
    )
    sentiment_score: int = Field(
        ge=-100,
        le=100,
        description="Numerical sentiment score from -100 (extreme negative) to +100 (extreme positive)",
    )
    key_catalysts: List[str] = Field(
        default_factory=list,
        description="Positive catalysts or growth drivers mentioned in news",
    )
    key_risks: List[str] = Field(
        default_factory=list,
        description="Negative news risks or reputational concerns",
    )
    news_summary: str = Field(
        description="Executive summary of analyzed news items"
    )


class FinalDecisionSchema(BaseModel):
    """Aggregate decision and executive report schema."""

    recommendation: Literal["PASS", "WATCHLIST", "REJECT"] = Field(
        description="Final recommendation: PASS (top pick), WATCHLIST, or REJECT (risk/low value)"
    )
    total_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Calculated composite total score from 0.0 to 100.0",
    )
    executive_summary: str = Field(
        description="Comprehensive executive summary integrating financial, anti-fraud, and news findings"
    )

from typing import Any, Dict, List, Optional, TypedDict


class StockState(TypedDict, total=False):
    """Unified LangGraph workflow state passed between nodes."""

    ticker: str
    raw_data: Dict[str, Any]
    fraud_report: Optional[Dict[str, Any]]
    value_report: Optional[Dict[str, Any]]
    news_articles: Optional[List[Dict[str, str]]]
    sentiment_report: Optional[Dict[str, Any]]
    final_decision: Optional[Dict[str, Any]]
    error: Optional[str]

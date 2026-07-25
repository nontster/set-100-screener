import sys
import json
import argparse
from typing import Any, Dict
from langgraph.graph import StateGraph, START, END

from src.state import StockState
from src.nodes.fetch_data import fetch_data_node
from src.nodes.anti_fraud import anti_fraud_node
from src.nodes.value_screener import value_screener_node
from src.nodes.scrape_news import scrape_news_node
from src.nodes.news_sentiment import news_sentiment_node
from src.nodes.stock_classifier import stock_classifier_node
from src.nodes.final_reporter import final_reporter_node
from src.nodes.notification import notification_node


def build_stock_screener_graph():
    """Build and compile the LangGraph fan-out / fan-in multi-agent workflow."""
    builder = StateGraph(StockState)

    # Add nodes
    builder.add_node("fetch_data", fetch_data_node)
    builder.add_node("anti_fraud", anti_fraud_node)
    builder.add_node("value_screener", value_screener_node)
    builder.add_node("scrape_news", scrape_news_node)
    builder.add_node("news_sentiment", news_sentiment_node)
    builder.add_node("stock_classifier", stock_classifier_node)
    builder.add_node("final_reporter", final_reporter_node)
    builder.add_node("notification", notification_node)

    # Entry edge
    builder.add_edge(START, "fetch_data")

    # Fan-Out parallel branches from fetch_data
    builder.add_edge("fetch_data", "anti_fraud")
    builder.add_edge("fetch_data", "value_screener")
    builder.add_edge("fetch_data", "scrape_news")
    builder.add_edge("fetch_data", "stock_classifier")

    # News sub-branch
    builder.add_edge("scrape_news", "news_sentiment")

    # Fan-In join to final_reporter
    builder.add_edge("anti_fraud", "final_reporter")
    builder.add_edge("value_screener", "final_reporter")
    builder.add_edge("news_sentiment", "final_reporter")
    builder.add_edge("stock_classifier", "final_reporter")

    # Final notification and termination
    builder.add_edge("final_reporter", "notification")
    builder.add_edge("notification", END)

    return builder.compile()


# Global compiled graph instance
stock_screener_graph = build_stock_screener_graph()


def run_single_stock_screening(ticker: str, notify: bool = False) -> Dict[str, Any]:
    """Execute screening workflow for a single ticker."""
    initial_state: StockState = {"ticker": ticker}
    final_state = stock_screener_graph.invoke(initial_state)

    decision = final_state.get("final_decision") or {}
    fraud = final_state.get("fraud_report") or {}
    value = final_state.get("value_report") or {}
    sentiment = final_state.get("sentiment_report") or {}
    classification = final_state.get("classification_report") or {}

    return {
        "ticker": final_state.get("ticker", ticker),
        "recommendation": decision.get("recommendation", "N/A"),
        "total_score": decision.get("total_score", 0.0),
        "fraud_risk_level": fraud.get("fraud_risk_level", "N/A"),
        "value_score": value.get("score", 0),
        "sentiment_score": sentiment.get("sentiment_score", 0),
        "overall_sentiment": sentiment.get("overall_sentiment", "N/A"),
        "executive_summary": decision.get("executive_summary", ""),
        "raw_data": final_state.get("raw_data", {}),
        "fraud_report": fraud,
        "value_report": value,
        "sentiment_report": sentiment,
        "classification_report": classification,
    }


def main():
    """CLI Entry point for single stock screening."""
    parser = argparse.ArgumentParser(
        description="SET100 AI Stock Screener & Anti-Fraud Suite"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Thai stock ticker symbol (e.g. CPALL, PTT)",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Dispatch push notifications for PASS recommendations",
    )

    args = parser.parse_args()
    result = run_single_stock_screening(args.ticker, notify=args.notify)

    output = {
        "ticker": result["ticker"],
        "recommendation": result["recommendation"],
        "total_score": result["total_score"],
        "fraud_risk_level": result["fraud_risk_level"],
        "value_score": result["value_score"],
        "sentiment_score": result["sentiment_score"],
        "executive_summary": result["executive_summary"],
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()

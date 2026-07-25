from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import StockState
from src.schemas import FinalDecisionSchema
from src.config import Config


def final_reporter_node(state: StockState) -> Dict[str, Any]:
    """
    Synthesis Fan-In Join Node: Aggregates evaluation results from Anti-Fraud, Value,
    and News Sentiment branches.
    Enforces total score formula, Anti-Fraud override rules, and sentiment risk gates.
    """
    ticker = state.get("ticker", "UNKNOWN")
    fraud_report = state.get("fraud_report") or {}
    value_report = state.get("value_report") or {}
    sentiment_report = state.get("sentiment_report") or {}

    fraud_risk = fraud_report.get("fraud_risk_level", "LOW").upper()
    value_score = float(value_report.get("score", 50))
    sentiment_score = float(sentiment_report.get("sentiment_score", 0))

    # Calculate Fraud Penalty
    fraud_penalty = 0.0
    if fraud_risk == "MEDIUM":
        fraud_penalty = 20.0
    elif fraud_risk == "HIGH":
        fraud_penalty = 50.0

    # Total Score Formula: (Value Score * 0.7) + (((Sentiment Score + 100) / 2) * 0.3) - Fraud Penalty
    normalized_sentiment = (sentiment_score + 100.0) / 2.0  # Maps -100..+100 -> 0..100
    raw_total_score = (value_score * 0.7) + (normalized_sentiment * 0.3) - fraud_penalty
    total_score = round(max(0.0, min(100.0, raw_total_score)), 1)

    # Decision Logic Evaluation
    recommendation = "WATCHLIST"

    # Rule 1: Safety & Anti-Fraud Override First (HIGH fraud risk -> Mandatory REJECT)
    if fraud_risk == "HIGH":
        recommendation = "REJECT"

    # Rule 2: Severe negative sentiment override (Sentiment < -50)
    elif sentiment_score < -50:
        recommendation = "REJECT" if total_score < 40 else "WATCHLIST"

    # Rule 3: Low fraud risk + high value score + acceptable sentiment -> PASS
    elif fraud_risk == "LOW" and value_score >= 70 and sentiment_score >= -20:
        recommendation = "PASS"

    # Rule 4: All other combinations -> WATCHLIST
    else:
        recommendation = "WATCHLIST"

    # Executive Summary Generation
    company_name = state.get("raw_data", {}).get("company_name", ticker)

    summary_text = (
        f"Analysis report for {company_name} ({ticker}): "
        f"Recommendation is {recommendation} with a Total Score of {total_score}/100. "
        f"Fraud Risk: {fraud_risk}, Value Score: {int(value_score)}/100, Sentiment Score: {int(sentiment_score)}. "
        f"Valuation Status: {value_report.get('valuation_status', 'N/A')}. "
    )

    if fraud_report.get("red_flags"):
        summary_text += f"Red Flags: {'; '.join(fraud_report['red_flags'])}. "

    if Config.GOOGLE_API_KEY:
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.2,
            )

            prompt = f"""
            You are the Chief Investment Officer (CIO) summarizing an investment evaluation for Thai stock {company_name} ({ticker}).
            Key Metrics:
            - Final Recommendation: {recommendation}
            - Total Score: {total_score}/100
            - Fraud Risk Level: {fraud_risk} (Red Flags: {fraud_report.get('red_flags', [])})
            - Value Score: {value_score}/100 (Status: {value_report.get('valuation_status', 'N/A')})
            - News Sentiment Score: {sentiment_score} ({sentiment_report.get('overall_sentiment', 'N/A')})
            - News Summary: {sentiment_report.get('news_summary', '')}

            Draft a concise, professional 3-4 sentence CIO executive summary explaining the rationale for the {recommendation} recommendation.
            """

            response = llm.invoke(prompt)
            if response and response.content:
                summary_text = response.content.strip()

        except Exception as e:
            print(f"Warning: Gemini API summary generation failed for {ticker}: {e}")

    final_decision = FinalDecisionSchema(
        recommendation=recommendation,
        total_score=total_score,
        executive_summary=summary_text,
    )

    return {"final_decision": final_decision.model_dump()}

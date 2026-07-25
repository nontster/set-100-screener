from typing import Any, Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import StockState
from src.schemas import StockClassificationSchema
from src.config import Config

MEGA_TREND_TAXONOMY = {
    "AI & Data Center Infrastructure": [
        "data center", "datacenter", "ai", "artificial intelligence", "cloud",
        "hyperscale", "server", "semiconductor", "supercomputing", "data hub",
        "telecom infrastructure", "ai power"
    ],
    "EV & Renewable Energy": [
        "ev", "electric vehicle", "solar", "wind", "battery", "renewable",
        "clean energy", "green energy", "grid", "power plant", "ev charger"
    ],
    "Healthcare & Aging Society": [
        "hospital", "healthcare", "medical", "wellness", "pharma", "aging",
        "elderly", "medical tourism", "patient care"
    ],
    "Digital Commerce & Smart Logistics": [
        "e-commerce", "logistics", "warehouse", "supply chain", "digital payment",
        "fintech", "express delivery", "smart warehouse"
    ],
}


def calculate_quantitative_metrics(raw_data: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Extracts and computes verified quantitative metrics for stock classification."""
    dividend_yield = raw_data.get("dividend_yield")
    payout_ratio = raw_data.get("payout_ratio")
    rev_cagr_3yr = raw_data.get("rev_cagr_3yr")
    eps_cagr_3yr = raw_data.get("eps_cagr_3yr")
    roe = raw_data.get("roe")

    # If payout ratio is missing but we have dividend yield and ROE/PE, estimate payout ratio safely
    if payout_ratio is None and dividend_yield is not None:
        pe = raw_data.get("pe_ratio")
        if pe is not None and pe > 0:
            # Dividend Yield = (DPS/Price), PE = (Price/EPS) -> Payout Ratio = Yield * PE / 100
            payout_ratio = (dividend_yield * pe)

    return {
        "dividend_yield": round(dividend_yield, 2) if dividend_yield is not None else None,
        "payout_ratio": round(payout_ratio, 2) if payout_ratio is not None else None,
        "rev_cagr_3yr": round(rev_cagr_3yr, 2) if rev_cagr_3yr is not None else None,
        "eps_cagr_3yr": round(eps_cagr_3yr, 2) if eps_cagr_3yr is not None else None,
        "roe": round(roe, 2) if roe is not None else None,
    }


def evaluate_mega_trends(
    raw_data: Dict[str, Any],
    news_articles: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Identifies alignment with World Mega Trends based on sector, industry, and news catalysts."""
    company_name = str(raw_data.get("company_name", "")).lower()
    sector = str(raw_data.get("sector", "")).lower()
    industry = str(raw_data.get("industry", "")).lower()

    text_corpus = f"{company_name} {sector} {industry}"
    if news_articles:
        for article in news_articles:
            title = article.get("title", "").lower()
            summary = article.get("snippet", "").lower() or article.get("summary", "").lower()
            text_corpus += f" {title} {summary}"

    matched_trends = []
    total_matches = 0

    for trend, keywords in MEGA_TREND_TAXONOMY.items():
        matches = [kw for kw in keywords if kw in text_corpus]
        if matches:
            matched_trends.append(trend)
            total_matches += len(matches)

    mega_trend_score = min(100, total_matches * 25)

    return {
        "mega_trends": matched_trends,
        "mega_trend_score": mega_trend_score,
    }


def calculate_classification_scores(
    metrics: Dict[str, Optional[float]],
    mega_trend_data: Dict[str, Any],
    fraud_risk_level: str,
    free_cash_flow: Optional[float] = None
) -> Dict[str, Any]:
    """Calculates deterministic classification scores, payout safety, and stock category."""
    # Safety Override Gate
    if fraud_risk_level == "HIGH":
        return {
            "category": "REJECTED",
            "dividend_score": 0,
            "growth_score": 0,
            "payout_safety": "UNSAFE",
            "mega_trends": mega_trend_data.get("mega_trends", []),
            "mega_trend_score": mega_trend_data.get("mega_trend_score", 0),
            "rationale": "FORCED OVERRIDE: Stock exhibits HIGH forensic accounting risk. Recommending REJECTED regardless of dividend or growth metrics.",
        }

    div_yield = metrics.get("dividend_yield")
    payout_ratio = metrics.get("payout_ratio")
    rev_cagr = metrics.get("rev_cagr_3yr")
    eps_cagr = metrics.get("eps_cagr_3yr")
    roe = metrics.get("roe")

    # Dividend Scoring & Payout Safety
    div_score = 30  # Baseline
    payout_safety = "NOT_APPLICABLE"

    if div_yield is not None:
        if div_yield >= 5.0:
            div_score += 45
        elif div_yield >= 4.0:
            div_score += 35
        elif div_yield >= 2.5:
            div_score += 20
        elif div_yield < 1.0:
            div_score -= 15

    if payout_ratio is not None:
        if payout_ratio <= 75.0:
            payout_safety = "SAFE"
            div_score += 25
        elif payout_ratio <= 90.0:
            payout_safety = "CAUTION"
            div_score += 10
        else:
            payout_safety = "UNSAFE"
            div_score -= 25

    if free_cash_flow is not None and free_cash_flow < 0 and div_yield and div_yield > 2.0:
        payout_safety = "UNSAFE"
        div_score -= 20

    dividend_score = max(0, min(100, int(div_score)))

    # Growth Scoring
    growth_base = 30  # Baseline
    mega_trend_score = mega_trend_data.get("mega_trend_score", 0)

    if rev_cagr is not None:
        if rev_cagr >= 15.0:
            growth_base += 35
        elif rev_cagr >= 10.0:
            growth_base += 25
        elif rev_cagr >= 5.0:
            growth_base += 10
        elif rev_cagr < 0:
            growth_base -= 15

    if eps_cagr is not None:
        if eps_cagr >= 15.0:
            growth_base += 25
        elif eps_cagr >= 10.0:
            growth_base += 15

    if roe is not None and roe >= 15.0:
        growth_base += 15

    if mega_trend_score >= 50:
        growth_base += 25
    elif mega_trend_score > 0:
        growth_base += 10

    growth_score = max(0, min(100, int(growth_base)))

    # Category Determination
    category = "NEUTRAL"
    if dividend_score >= 70 and growth_score >= 70:
        category = "HYBRID"
    elif dividend_score >= 70:
        category = "DIVIDEND"
    elif growth_score >= 70:
        category = "GROWTH"

    # Default Rationale Template
    rationale_parts = []
    if category == "DIVIDEND":
        rationale_parts.append(f"Strong dividend profile (Yield: {div_yield if div_yield else 'N/A'}%, Safety: {payout_safety}).")
    elif category == "GROWTH":
        rationale_parts.append(f"High growth momentum (Growth Score: {growth_score}/100).")
    elif category == "HYBRID":
        rationale_parts.append(f"Dual-benefit stock offering both attractive dividend yield and growth momentum.")
    else:
        rationale_parts.append(f"Balanced/Neutral fundamental profile (Div Score: {dividend_score}, Growth Score: {growth_score}).")

    if mega_trend_data.get("mega_trends"):
        trends_str = ", ".join(mega_trend_data["mega_trends"])
        rationale_parts.append(f"Aligned with World Mega Trends: {trends_str}.")

    rationale = " ".join(rationale_parts)

    return {
        "category": category,
        "dividend_score": dividend_score,
        "growth_score": growth_score,
        "payout_safety": payout_safety,
        "mega_trends": mega_trend_data.get("mega_trends", []),
        "mega_trend_score": mega_trend_score,
        "rationale": rationale,
    }


def stock_classifier_node(state: StockState) -> Dict[str, Any]:
    """
    LangGraph Node: Classifies stock into DIVIDEND, GROWTH, HYBRID, NEUTRAL, or REJECTED
    using quantitative metrics, World Mega Trend alignment, and LLM rationale synthesis.
    """
    ticker = state.get("ticker", "UNKNOWN")
    raw_data = state.get("raw_data", {})
    fraud_report = state.get("fraud_report") or {}
    news_articles = state.get("news_articles") or []

    fraud_risk_level = fraud_report.get("fraud_risk_level", "LOW")
    free_cash_flow = raw_data.get("free_cash_flow")

    # Step 1: Calculate quantitative metrics
    metrics = calculate_quantitative_metrics(raw_data)

    # Step 2: Evaluate Mega Trends
    mega_trend_data = evaluate_mega_trends(raw_data, news_articles)

    # Step 3: Compute baseline classification & score
    scores = calculate_classification_scores(
        metrics=metrics,
        mega_trend_data=mega_trend_data,
        fraud_risk_level=fraud_risk_level,
        free_cash_flow=free_cash_flow,
    )

    # Step 4: Synthesize LLM executive rationale if API key is present
    if Config.GOOGLE_API_KEY and fraud_risk_level != "HIGH":
        try:
            llm = ChatGoogleGenerativeAI(
                model=Config.get_gemini_model(),
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.1,
            )
            structured_llm = llm.with_structured_output(StockClassificationSchema)

            prompt = f"""
            You are a senior investment strategist evaluating Thai stock {ticker}.
            Classification Data:
            - Assigned Category: {scores['category']}
            - Dividend Score: {scores['dividend_score']}/100 (Yield: {metrics.get('dividend_yield')}%, Payout Ratio: {metrics.get('payout_ratio')}%)
            - Payout Safety: {scores['payout_safety']}
            - Growth Score: {scores['growth_score']}/100 (Rev CAGR: {metrics.get('rev_cagr_3yr')}%, EPS CAGR: {metrics.get('eps_cagr_3yr')}%, ROE: {metrics.get('roe')}%)
            - World Mega Trends Aligned: {scores['mega_trends']} (Score: {scores['mega_trend_score']}/100)

            Generate a concise, factual executive rationale explaining the stock's classification and highlighting its dividend safety and/or mega-trend growth drivers.
            Output a valid StockClassificationSchema object.
            """

            result: StockClassificationSchema = structured_llm.invoke(prompt)
            # Ensure deterministic category and scores are preserved
            report_dict = result.model_dump()
            report_dict["category"] = scores["category"]
            report_dict["dividend_score"] = scores["dividend_score"]
            report_dict["growth_score"] = scores["growth_score"]
            report_dict["payout_safety"] = scores["payout_safety"]
            report_dict["mega_trends"] = scores["mega_trends"]
            report_dict["mega_trend_score"] = scores["mega_trend_score"]
            report_dict["metrics"] = metrics

            return {"classification_report": report_dict}

        except Exception as e:
            print(f"Warning: Gemini API call failed in stock_classifier_node for {ticker}: {e}")

    # Fallback response
    fallback_schema = StockClassificationSchema(
        ticker=ticker,
        category=scores["category"],
        dividend_score=scores["dividend_score"],
        growth_score=scores["growth_score"],
        payout_safety=scores["payout_safety"],
        mega_trends=scores["mega_trends"],
        mega_trend_score=scores["mega_trend_score"],
        rationale=scores["rationale"],
        metrics=metrics,
    )

    return {"classification_report": fallback_schema.model_dump()}

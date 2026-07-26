from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import StockState
from src.schemas import ValueAnalysisSchema
from src.config import Config


def value_screener_node(state: StockState) -> Dict[str, Any]:
    """
    Branch B Node: Evaluates value parameters, profitability ratios, and balance sheet quality.
    Outputs ValueAnalysisSchema (score 0-100, valuation_status, key_strengths, key_weaknesses).
    """
    ticker = state.get("ticker", "UNKNOWN")
    raw_data = state.get("raw_data", {})

    # Deterministic scoring calculation
    roe = raw_data.get("roe")
    pe = raw_data.get("pe_ratio")
    pb = raw_data.get("pb_ratio")
    fcf = raw_data.get("free_cash_flow")
    cfo = raw_data.get("operating_cash_flow")
    current_ratio = raw_data.get("current_ratio")

    score = 50  # Base score
    strengths = []
    weaknesses = []

    if roe is not None:
        if roe >= 15:
            score += 20
            strengths.append(f"Strong Return on Equity (ROE: {roe:.1f}%)")
        elif roe >= 10:
            score += 10
            strengths.append(f"Acceptable ROE ({roe:.1f}%)")
        elif roe < 5:
            score -= 15
            weaknesses.append(f"Low profitability (ROE: {roe:.1f}%)")

    if pe is not None:
        if 0 < pe <= 15:
            score += 15
            strengths.append(f"Attractive P/E ratio ({pe:.1f}x)")
        elif pe > 30:
            score -= 10
            weaknesses.append(f"Elevated P/E valuation ({pe:.1f}x)")

    if fcf is not None and fcf > 0:
        score += 10
        strengths.append("Positive Free Cash Flow")
    elif fcf is not None and fcf < 0:
        score -= 10
        weaknesses.append("Negative Free Cash Flow")

    if current_ratio is not None:
        if current_ratio >= 1.5:
            score += 5
            strengths.append(f"Strong current ratio ({current_ratio:.2f})")
        elif current_ratio < 1.0:
            score -= 10
            weaknesses.append(f"Liquidity concern: Current ratio < 1.0 ({current_ratio:.2f})")

    # Clamp score to 0-100 range
    final_score = max(0, min(100, int(score)))
    is_value = final_score >= 70

    if Config.GOOGLE_API_KEY:
        try:
            llm = ChatGoogleGenerativeAI(
                model=Config.get_gemini_model(),
                google_api_key=Config.GOOGLE_API_KEY,
            )
            structured_llm = llm.with_structured_output(ValueAnalysisSchema)

            prompt = f"""
            You are a fundamental value investing analyst evaluating Thai stock {ticker}.
            Analyze the following parameters:
            - ROE: {roe}%
            - P/E Ratio: {pe}
            - P/BV Ratio: {pb}
            - Free Cash Flow: {fcf}
            - Operating Cash Flow: {cfo}
            - Current Ratio: {current_ratio}
            - Dividend Yield: {raw_data.get('dividend_yield')}%

            Calculated Baseline Score: {final_score}/100

            Evaluate value metrics and output a structured ValueAnalysisSchema.
            """

            result: ValueAnalysisSchema = structured_llm.invoke(prompt)
            return {"value_report": result.model_dump()}

        except Exception as e:
            print(f"Warning: Gemini API call failed in value_screener_node for {ticker}: {e}")

    # Fallback status
    status = "FAIRLY_VALUED"
    if final_score >= 75:
        status = "UNDERVALUED"
    elif final_score <= 45:
        status = "OVERVALUED"

    fallback_report = ValueAnalysisSchema(
        is_value_stock=is_value,
        score=final_score,
        valuation_status=status,
        key_strengths=strengths,
        key_weaknesses=weaknesses,
    )

    return {"value_report": fallback_report.model_dump()}

from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import StockState
from src.schemas import FraudAnalysisSchema
from src.config import Config


def anti_fraud_node(state: StockState) -> Dict[str, Any]:
    """
    Branch A Node: Evaluates forensic accounting risks, cash flow quality, and red flags.
    Uses Gemini structured output (FraudAnalysisSchema) or deterministic rules.
    """
    ticker = state.get("ticker", "UNKNOWN")
    raw_data = state.get("raw_data", {})

    # Deterministic rule checks (pre-audit)
    net_income = raw_data.get("net_income")
    cfo = raw_data.get("operating_cash_flow")
    de_ratio = raw_data.get("de_ratio")

    deterministic_flags = []
    if net_income is not None and cfo is not None:
        if net_income > 0 and cfo < 0:
            deterministic_flags.append(
                "Severe divergence: Positive Net Income with Negative Operating Cash Flow (CFO)."
            )
    if de_ratio is not None and de_ratio > 3.0:
        deterministic_flags.append(
            f"Excessively high leverage ratio: D/E ratio = {de_ratio:.2f} > 3.0"
        )

    # Use Gemini structured output if API key is set
    if Config.GOOGLE_API_KEY:
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.1,
            )
            structured_llm = llm.with_structured_output(FraudAnalysisSchema)

            prompt = f"""
            You are a senior forensic accountant auditing Thai stock {ticker}.
            Analyze the following financial metrics:
            - Net Income: {net_income}
            - Operating Cash Flow (CFO): {cfo}
            - Free Cash Flow (FCF): {raw_data.get('free_cash_flow')}
            - Debt to Equity (D/E): {de_ratio}
            - Current Ratio: {raw_data.get('current_ratio')}
            - P/E Ratio: {raw_data.get('pe_ratio')}

            Deterministic Anomalies Identified: {deterministic_flags}

            Assess accounting risk:
            - HIGH: If severe CFO vs Net Income divergence exists, high debt coverage risk, or major red flags.
            - MEDIUM: Moderate accounting concerns or missing key cash flow data.
            - LOW: Healthy alignment between CFO and Net Income, manageable debt.

            Return a structured FraudAnalysisSchema.
            """

            result: FraudAnalysisSchema = structured_llm.invoke(prompt)
            return {"fraud_report": result.model_dump()}

        except Exception as e:
            print(f"Warning: Gemini API call failed in anti_fraud_node for {ticker}: {e}")

    # Deterministic fallback when API key unconfigured or call fails
    risk_level = "LOW"
    if deterministic_flags:
        risk_level = "HIGH" if "Severe divergence" in "".join(deterministic_flags) else "MEDIUM"

    fallback_report = FraudAnalysisSchema(
        fraud_risk_level=risk_level,
        cash_flow_quality=(
            "Operating cash flow appears aligned with earnings."
            if risk_level == "LOW"
            else "Potential cash flow quality issues detected."
        ),
        red_flags=deterministic_flags,
        reasoning=(
            "Rule-based deterministic fallback evaluation."
            if not deterministic_flags
            else f"Rule-based flags: {'; '.join(deterministic_flags)}"
        ),
    )

    return {"fraud_report": fallback_report.model_dump()}

# Phase 1 Data Model: Dividend vs. Growth Stock Analysis

**Feature Branch**: `002-dividend-growth-analysis`
**Date**: 2026-07-26
**Spec**: [spec.md](file:///Users/nontster/git/set-100-screener/specs/002-dividend-growth-analysis/spec.md)

## Entities & Data Schemas

### 1. `StockCategory` (Enum)

Defines the classification category assigned to a stock.

| Value | Description |
|-------|-------------|
| `DIVIDEND` | High, sustainable dividend yield stock (Yield ≥ 4%, Payout Ratio ≤ 85%) |
| `GROWTH` | High historical CAGR stock (Revenue/EPS ≥ 10%) or high Mega Trend positioning |
| `HYBRID` | Meets both Dividend and Growth stock criteria |
| `NEUTRAL` | Does not meet Dividend or Growth stock threshold baselines |
| `REJECTED` | High accounting risk / fraud flag override applied (Safety First) |

---

### 2. `PayoutSafetyStatus` (Enum)

Defines the dividend safety evaluation.

| Value | Description |
|-------|-------------|
| `SAFE` | Dividend covered by Operating Cash Flow & Payout Ratio ≤ 80% |
| `CAUTION` | Payout Ratio between 80% and 100%, or declining cash flow coverage |
| `UNSAFE` | Dividend unsustainably paid out of debt/reserves (Payout > 100% or negative FCF) |
| `NOT_APPLICABLE` | Non-dividend paying stock |

---

### 3. `MegaTrendCategory` (Literal String Enum)

Taxonomy of recognized World Mega Trends.

- `"AI & Data Center Infrastructure"`
- `"EV & Renewable Energy"`
- `"Healthcare & Aging Society"`
- `"Digital Commerce & Smart Logistics"`
- `"None / Traditional Sector"`

---

### 4. `StockClassificationSchema` (Pydantic Model)

Pydantic model for node output and API serialization.

```python
class StockClassificationSchema(BaseModel):
    ticker: str = Field(description="Ticker symbol e.g. ADVANC.BK")
    category: Literal["DIVIDEND", "GROWTH", "HYBRID", "NEUTRAL", "REJECTED"] = Field(
        description="Assigned stock classification category"
    )
    dividend_score: int = Field(ge=0, le=100, description="Dividend score from 0 to 100")
    growth_score: int = Field(ge=0, le=100, description="Growth score from 0 to 100")
    payout_safety: Literal["SAFE", "CAUTION", "UNSAFE", "NOT_APPLICABLE"] = Field(
        description="Dividend payout safety assessment"
    )
    mega_trends: List[str] = Field(
        default_factory=list,
        description="List of identified World Mega Trend alignment tags"
    )
    mega_trend_score: int = Field(ge=0, le=100, description="Mega Trend alignment score from 0 to 100")
    rationale: str = Field(description="LLM-synthesized executive summary rationale")
    metrics: Dict[str, Optional[float]] = Field(
        description="Verified metrics: dividend_yield, payout_ratio, rev_cagr_3yr, eps_cagr_3yr, roe"
    )
```

---

### 5. `GraphState` Extensions

Extension to the central `GraphState` in `src/state.py`:

```python
class GraphState(TypedDict, total=False):
    # Existing fields: ticker, financial_data, fraud_analysis, value_analysis, news_sentiment, final_decision
    classification_analysis: Dict[str, Any]  # Serialized StockClassificationSchema
```

---

## Validation & Business Rules

1. **Safety Override Gate**:
   - `IF fraud_analysis.fraud_risk_level == "HIGH" THEN category = "REJECTED" AND rationale MUST cite fraud override.`
2. **Dividend Safety Rule**:
   - `IF dividend_yield >= 0.04 AND payout_ratio <= 0.85 THEN dividend_score >= 70.`
   - `IF payout_ratio > 1.00 OR free_cash_flow < 0 THEN payout_safety = "UNSAFE".`
3. **Growth & Mega Trend Rule**:
   - `IF rev_cagr_3yr >= 0.10 OR eps_cagr_3yr >= 0.12 OR mega_trend_score >= 75 THEN growth_score >= 70.`
4. **Zero Hallucination Rule**:
   - Missing fields in `metrics` dictionary MUST explicitly store `None` (`Data Missing`) and never invent random numbers.

# Quickstart Validation Guide: Dividend vs. Growth Stock Analysis

**Feature Branch**: `002-dividend-growth-analysis`
**Date**: 2026-07-26
**Spec**: [spec.md](file:///Users/nontster/git/set-100-screener/specs/002-dividend-growth-analysis/spec.md)

This guide documents runnable validation scenarios that prove the feature works end-to-end.

## Prerequisites

1. Active Python environment with required dependencies installed (`pip install -r requirements.txt`).
2. `.env` file configured with `GOOGLE_API_KEY` for Gemini LLM synthesis.

## Runnable Validation Scenarios

### Scenario 1: Unit Test & Classification Logic Verification

Run pytest on the classifier node unit test suite:

```bash
pytest tests/unit/test_stock_classifier.py -v
```

**Expected Result**: All tests pass, validating that:
- High dividend stock with safe payout ratio is classified as `DIVIDEND`.
- High growth / Mega Trend aligned stock (e.g. Data Center provider) is classified as `GROWTH`.
- Stock meeting both dividend & growth criteria is classified as `HYBRID`.
- High fraud risk stock (`fraud_risk_level = HIGH`) is forcibly overridden to `REJECTED`.

---

### Scenario 2: Single Stock Analysis CLI Run

Run single-ticker screener execution for a known SET stock (e.g., ADVANC.BK or DELTA.BK):

```bash
python -m src.graph ADVANC.BK
```

**Expected Result**:
- The console log confirms execution of `stock_classifier_node`.
- Output JSON includes `classification_analysis` with category, scores, Mega Trend tags, and executive rationale.

---

### Scenario 3: Streamlit UI Dashboard Verification

Launch the Streamlit dashboard:

```bash
streamlit run src/app.py
```

**Expected Result**:
- Screening report table displays `Stock Category`, `Payout Safety`, `Mega Trend Tags`, and `Classification Rationale`.
- Category sidebar filter allows filtering by `DIVIDEND`, `GROWTH`, `HYBRID`, or `Mega Trend` tags cleanly.

# Implementation Plan: Dividend vs. Growth Stock Analysis & Classification

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Branch**: `002-dividend-growth-analysis` | **Date**: 2026-07-26 | **Spec**: [spec.md](file:///Users/nontster/git/set-100-screener/specs/002-dividend-growth-analysis/spec.md)

**Input**: Feature specification from `/specs/002-dividend-growth-analysis/spec.md`

## Summary

Implement automated stock categorization (`DIVIDEND`, `GROWTH`, `HYBRID`, `NEUTRAL`, `REJECTED`) for SET100 tickers using a hybrid architecture: pure Python quantitative metric calculation (Yield, Payout Safety, 3-Yr CAGR) combined with `gemini-3.6-flash` structured output synthesis for World Mega Trend alignment (AI & Data Centers, EV & Renewable Energy, Healthcare, Smart Logistics) and executive rationale generation.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: LangGraph, LangChain Google GenAI (`gemini-3.6-flash` with `with_structured_output`), Pydantic v2, yfinance, pandas, openpyxl, streamlit, plotly  
**Storage**: File exports (CSV with UTF-8-SIG, Excel `.xlsx`), local JSON cache (`src/cache.py`)  
**Testing**: pytest  
**Target Platform**: macOS / Linux server / Streamlit web dashboard  
**Project Type**: Multi-Agent Financial Screener & Analytics Web Application  
**Performance Goals**: Client-side filtering in Streamlit dashboard < 0.5s; single-ticker analysis runtime within standard LangGraph node latency limits  
**Constraints**: 0% numerical hallucination (Constitution II); Safety & Anti-Fraud override MUST take precedence over dividend/growth recommendation (Constitution I)  
**Scale/Scope**: SET100 universe (100 tickers per screening run)  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Safety & Anti-Fraud Override First**: If `anti_fraud` node flags stock as `HIGH` risk, classifier forcibly assigns category `REJECTED (Accounting/Fraud Risk)`.
- [x] **II. Data Rigor & Zero Hallucination**: Financial figures parsed directly from verified yfinance sources; missing metrics explicitly stored as `None` / `Data Missing`.
- [x] **III. Parallel Multi-Agent Architecture**: Decoupled `stock_classifier` single-responsibility node added to LangGraph workflow.
- [x] **IV. Thai Stock Market Specialization**: Tickers mapped with `.BK` suffix; exports encoded with UTF-8-SIG.
- [x] **V. Resilience & Fault Tolerance**: Single stock calculation or LLM API failure caught gracefully to allow batch runs to complete.

## Project Structure

### Documentation (this feature)

```text
specs/002-dividend-growth-analysis/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── classification_contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code Layout

```text
src/
├── schemas.py           # Extended with StockClassificationSchema
├── state.py             # Extended GraphState with classification_analysis
├── graph.py             # Updated LangGraph workflow to include stock_classifier node
├── nodes/
│   ├── stock_classifier.py  # NEW: Quantitative classification + Mega Trend & LLM rationale node
│   ├── final_reporter.py    # Updated report aggregator to include classification columns
│   └── ...
├── batch.py             # Updated CSV/Excel export formatting
└── app.py               # Streamlit UI updated with category & mega trend filters

tests/
├── unit/
│   └── test_stock_classifier.py  # Unit tests for classification rules & safety override
└── integration/
    └── test_classification_pipeline.py  # End-to-end node integration tests
```

**Structure Decision**: Single project layout adhering to existing `src/` and `tests/` structure.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | Structure aligns strictly with Constitution and existing design. | N/A |

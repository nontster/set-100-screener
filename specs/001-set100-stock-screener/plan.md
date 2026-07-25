# Implementation Plan: SET100 AI Stock Screener & Anti-Fraud Suite

**Branch**: `001-set100-stock-screener` | **Date**: 2026-07-25 | **Spec**: [spec.md](file:///Users/nontster/git/set-100-screener/specs/001-set100-stock-screener/spec.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Input**: Feature specification from `/specs/001-set100-stock-screener/spec.md`

## Summary

Build a multi-agent AI stock screening system for SET100 Thai stocks using LangGraph with fan-out/fan-in parallel execution. The system fetches financial data via `yfinance`, runs three parallel evaluation branches (Anti-Fraud forensic audit, Value Screener, News Sentiment via Google News RSS + Gemini), synthesizes a final recommendation (PASS/WATCHLIST/REJECT) with a weighted scoring formula, and surfaces results through a Streamlit dashboard with Plotly charts, push notifications (Telegram + LINE), automated post-market batch runs, and Excel/CSV report exports.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: LangGraph, LangChain Google GenAI (`gemini-3.6-flash`), `yfinance`, `requests`, `beautifulsoup4`, `pydantic` (v2), `pandas`, `openpyxl`, `apscheduler`, `pytz`, `streamlit`, `plotly`, `python-dotenv`, `tqdm`

**Storage**: File-based JSON cache (12-hour TTL) for `yfinance` data; Excel/CSV exports for batch reports

**Testing**: `pytest` with mocked `yfinance`/API responses

**Target Platform**: macOS/Linux (Python 3.10+), local dev + deployment

**Project Type**: Multi-agent AI pipeline + web dashboard

**Performance Goals**: Full SET100 batch (<100 tickers) completes in under 10 minutes with 3 parallel workers

**Constraints**: Rate-limited API calls (yfinance, Google News RSS, Gemini); Thai text encoding (UTF-8-SIG); timezone-locked scheduling (Asia/Bangkok ICT)

**Scale/Scope**: ~100 SET tickers per batch; single-user Streamlit dashboard; 2 notification channels

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Safety & Anti-Fraud Override First | ✅ PASS | FR-005: HIGH fraud risk → mandatory REJECT. FR-006/FR-007: scoring formula includes fraud penalty. Decision logic in `final_reporter` node enforces override before any valuation consideration. |
| II | Data Rigor & Zero Hallucination | ✅ PASS | FR-002: metrics parsed strictly from `yfinance`; missing data tagged `N/A` / `Data Missing`. Gemini calls use `with_structured_output` (pydantic v2 schemas) — LLM cannot return free-form numbers. |
| III | Parallel Multi-Agent Architecture | ✅ PASS | FR-004: LangGraph fan-out/fan-in graph with single-responsibility nodes (fetch → [anti_fraud ∥ value_screener ∥ scrape_news → sentiment] → final_reporter → notification). |
| IV | Thai Stock Market Specialization | ✅ PASS | FR-001: `.BK` suffix mapping. FR-009: Thai news query `{ticker} หุ้น`. FR-012: UTF-8-SIG CSV encoding. Thai text preserved end-to-end. |
| V | Resilience & Fault Tolerance | ✅ PASS | FR-003: 12-hour file cache. FR-011: rate-limited ThreadPoolExecutor. Edge cases: missing data → `N/A`, zero news → neutral sentiment, API failures → log-and-continue. |

**Gate Result**: ✅ ALL PRINCIPLES PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-set100-stock-screener/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── config.py              # Environment config loader (.env)
├── state.py               # StockState TypedDict definition
├── schemas.py             # Pydantic v2 output schemas
├── cache.py               # File-based JSON cache (12h TTL)
├── set100_tickers.py      # SET100 ticker list constant
├── nodes/
│   ├── fetch_data.py      # Entry node: yfinance data extraction
│   ├── anti_fraud.py      # Branch A: forensic accounting audit
│   ├── value_screener.py  # Branch B: value & profitability scoring
│   ├── scrape_news.py     # Branch C1: Google News RSS scraper
│   ├── news_sentiment.py  # Branch C2: Gemini sentiment analysis
│   ├── final_reporter.py  # Fan-in synthesis + decision logic
│   └── notification.py    # Telegram + LINE dispatch
├── graph.py               # LangGraph workflow assembly
├── batch.py               # ThreadPoolExecutor batch runner + export
├── scheduler.py           # APScheduler cron job (17:00 ICT)
└── app.py                 # Streamlit dashboard entry point

tests/
├── unit/
│   ├── test_schemas.py
│   ├── test_cache.py
│   ├── test_scoring.py
│   └── test_decision_logic.py
└── integration/
    ├── test_graph_flow.py
    └── test_batch_pipeline.py
```

**Structure Decision**: Single-project flat structure. All source under `src/`, tests under `tests/`. The `nodes/` subdirectory groups LangGraph node functions by responsibility. Streamlit app is a single `app.py` entry point (standard for Streamlit). No backend/frontend split needed since Streamlit is a unified Python web framework.

## Complexity Tracking

> No constitution violations detected. No complexity justifications needed.

<!--
Sync Impact Report:
- Version change: Initial (Template) → 1.0.0
- List of modified principles:
  - Replaced [PRINCIPLE_1_NAME] → I. Safety & Anti-Fraud Override First
  - Replaced [PRINCIPLE_2_NAME] → II. Data Rigor & Zero Hallucination
  - Replaced [PRINCIPLE_3_NAME] → III. Parallel Multi-Agent Architecture
  - Replaced [PRINCIPLE_4_NAME] → IV. Thai Stock Market Specialization
  - Replaced [PRINCIPLE_5_NAME] → V. Resilience & Fault Tolerance
- Added sections:
  - Tech Stack & Standards
  - Code Quality & Formatting Guidelines
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ aligned)
  - .specify/templates/spec-template.md (✅ aligned)
  - .specify/templates/tasks-template.md (✅ aligned)
- Follow-up TODOs: None
-->

# SET100 AI Stock Screener & Anti-Fraud Suite Constitution

## Core Principles

### I. Safety & Anti-Fraud Override First
Financial integrity overrides valuation. If the system detects high accounting risk or fraud indicators, the stock MUST be flagged as REJECT regardless of how cheap or attractive its valuation metrics appear.

### II. Data Rigor & Zero Hallucination
AI Agents MUST operate under strict constraints. Numerical metrics MUST be parsed directly from verified sources (`yfinance`, SEC filings). The LLM is strictly prohibited from inventing financial figures; missing metrics MUST be explicitly marked as `N/A` or `Data Missing`.

### III. Parallel Multi-Agent Architecture
System components MUST be decoupled into single-responsibility nodes managed by a LangGraph workflow using Fan-out / Fan-in parallel execution to minimize latency.

### IV. Thai Stock Market Specialization
System MUST natively handle Thai stocks traded on the Stock Exchange of Thailand (SET 100 list) with proper ticker suffix mapping (`.BK`), Thai character encoding (`utf-8-sig`), and Thai financial news processing.

### V. Resilience & Fault Tolerance
Batch processing and scheduled jobs MUST handle API rate limits, network timeouts, and single-stock failures gracefully without crashing the pipeline. Node-level error handling (`try-except` blocks) MUST log errors and allow batch jobs to continue processing remaining stocks.

## Tech Stack & Standards

- **Primary Language**: Python 3.10+
- **Agent Orchestration**: LangGraph, LangChain Google GenAI (`gemini-3.6-flash` model with `with_structured_output`)
- **Data Extraction**: `yfinance` (financial statements & price data), `requests` + `beautifulsoup4` (Google News RSS Thai feed scraper)
- **Data Schemas**: `pydantic` (v2) models for strictly typed LLM outputs
- **Batch & Data Export**: `pandas`, `openpyxl` (Excel), UTF-8-SIG encoded CSV
- **Scheduling**: `apscheduler` with `pytz` (Timezone: `Asia/Bangkok`)
- **User Interface**: `streamlit`, `plotly`
- **Notification Services**: Telegram Bot API, LINE Messaging API

## Code Quality & Formatting Guidelines

- **Type Hinting**: Use explicit Python type hinting (`TypedDict`, `Optional`, `List`, `Dict`) for all graph state definitions and function signatures.
- **Error Handling**: Enforce strict error handling (`try-except` blocks) at node levels to allow batch jobs to log errors and continue processing.
- **Environment Configuration**: Maintain environment variable configuration using `.env` for keys (`GOOGLE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_USER_ID`).

## Governance

This constitution supersedes all other technical or architectural choices. All code reviews, specifications, implementation plans, and tasks MUST comply with these core principles and technology standards. Amendments require formal documentation, explicit rationale, semantic version incrementing, and updating of all dependent templates.

**Version**: 1.0.0 | **Ratified**: 2026-07-25 | **Last Amended**: 2026-07-25

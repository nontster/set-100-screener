# Phase 0 Research: Dividend vs. Growth Stock Analysis

**Feature Branch**: `002-dividend-growth-analysis`
**Date**: 2026-07-26
**Spec**: [spec.md](file:///Users/nontster/git/set-100-screener/specs/002-dividend-growth-analysis/spec.md)

## Research Findings & Architectural Decisions

### 1. Classification Strategy Architecture

- **Decision**: Hybrid Rule-Based Quantitative Thresholds + LLM Executive Rationale Synthesis (`gemini-3.6-flash` with Pydantic structured output).
- **Rationale**:
  - **Data Rigor**: All mathematical formulas (Dividend Yield, Payout Ratio, 3-Yr Revenue CAGR, 3-Yr EPS CAGR) are executed deterministically in pure Python node logic. This ensures zero risk of LLM hallucination on financial numbers, adhering strictly to **Constitution Principle II**.
  - **Narrative Value**: `gemini-3.6-flash` is leveraged via `with_structured_output` to synthesize factual, human-readable executive rationales and extract qualitative World Mega Trend drivers from news/company descriptions.
- **Alternatives Considered**:
  - *Pure Python Rule Engine without LLM*: Rejected because rationale descriptions would be mechanical string concatenations, losing strategic context.
  - *Full LLM-driven numerical analysis*: Rejected because LLMs can introduce numerical inconsistencies or hallucinate financial figures, violating Constitution Principle II.

---

### 2. World Mega Trend Alignment Scoring & Taxonomy

- **Decision**: Define a structured taxonomy of World Mega Trends in the system configuration and evaluate ticker alignment using company sector data, business summaries, and scraped financial news items (`scrape_news.py`).
- **Taxonomy**:
  1. `AI & Data Center Infrastructure`: Hyperscale data centers, cloud infrastructure, AI servers, specialized telecom & power utilities.
  2. `EV & Renewable Energy`: Solar, wind, battery storage, EV supply chain, grid modernization.
  3. `Healthcare & Aging Society`: Hospitals, medical devices, wellness tourism, pharmaceutical distribution.
  4. `Digital Commerce & Smart Logistics`: E-commerce infrastructure, automated warehousing, supply chain tech.
- **Rationale**: The SET (Stock Exchange of Thailand) includes traditional companies expanding into mega trend verticals (e.g., power utilities investing heavily in AI Data Center power supply, telecom operators building cloud data centers). Combining financial history with Mega Trend tags ensures high-potential growth candidates are correctly identified.

---

### 3. Pipeline Integration & Multi-Agent Graph Nodes

- **Decision**: Introduce a dedicated `stock_classifier` node in `src/nodes/stock_classifier.py` and register it in `src/graph.py`.
- **Data Flow**:
  1. `fetch_data` node retrieves yfinance financial statements & price data.
  2. `anti_fraud` node performs forensic accounting audit (checking OCF vs Net Income, red flags).
  3. `scrape_news` node gathers latest Thai financial news.
  4. `stock_classifier` node executes quantitative classification, runs Mega Trend scoring, checks anti-fraud risk override, and generates LLM rationale.
  5. `final_reporter` integrates classification data into screening summary reports and exports.
- **Rationale**: Decoupled single-responsibility node pattern adheres strictly to **Constitution Principle III (Parallel Multi-Agent Architecture)**.

---

### 4. Safety & Anti-Fraud Guardrails Integration

- **Decision**: Direct override enforcement inside `stock_classifier`.
- **Logic**: If `anti_fraud` risk level is `"HIGH"`, the stock's category is forcibly assigned to `REJECTED (Accounting/Fraud Risk)` with `payout_safety_status = "Unsafe"`, regardless of how high the dividend yield or growth rate appears.
- **Rationale**: Strictly complies with **Constitution Principle I (Safety & Anti-Fraud Override First)**.

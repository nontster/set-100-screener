# Requirements Quality Checklist: SET100 AI Stock Screener & Anti-Fraud Suite

**Purpose**: Validate specification completeness, clarity, consistency, and coverage before proceeding to task generation (`/speckit-tasks`) and implementation.
**Created**: 2026-07-25
**Feature**: [spec.md](file:///Users/nontster/git/set-100-screener/specs/001-set100-stock-screener/spec.md) | [plan.md](file:///Users/nontster/git/set-100-screener/specs/001-set100-stock-screener/plan.md)
**Audience**: Pre-Implementation Requirement Reviewer
**Depth**: Full Coverage (Strict)

---

## 1. Requirement Completeness

- [ ] CHK001 - Are raw data extraction metrics (P/E, P/BV, ROE, D/E Ratio, Free Cash Flow, Operating Cash Flow, Net Income, Dividend Yield, Current Ratio) explicitly specified without omission? [Completeness, Spec §FR-002]
- [ ] CHK002 - Is the 12-hour TTL cache expiration and file storage layout fully documented? [Completeness, Spec §FR-003, Research §R6]
- [ ] CHK003 - Are state attributes defined for every step of the multi-agent graph workflow in `StockState`? [Completeness, Data Model §StockState]
- [ ] CHK004 - Are output requirements specified for all four evaluation nodes (`anti_fraud_node`, `value_screener_node`, `scrape_news_node`, `news_sentiment_node`)? [Completeness, Spec §FR-004]
- [ ] CHK005 - Are required columns and Thai header formatting explicitly defined for Excel (`.xlsx`) and CSV exports? [Completeness, Spec §FR-012]
- [ ] CHK006 - Are environment configuration key names (`GOOGLE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_USER_ID`) documented with default fallback behaviors? [Completeness, Plan §Technical Context, Constitution §Tech Stack]

## 2. Requirement Clarity & Quantified Metrics

- [ ] CHK007 - Is the Total Score calculation formula mathematically defined with explicit weights, normalization ranges, and penalty subtractions? [Clarity, Spec §FR-006]
- [ ] CHK008 - Are exact threshold values specified for `PASS` qualification (Value Score >= 70, Sentiment Score >= -20, Fraud Risk == LOW)? [Clarity, Spec §FR-007]
- [ ] CHK009 - Is the news sentiment override trigger strictly quantified (`Sentiment Score < -50`)? [Clarity, Spec §FR-008]
- [ ] CHK010 - Is the daily post-market schedule trigger uniquely specified with time (`17:00 ICT`), frequency (`Mon-Fri`), and timezone (`Asia/Bangkok`)? [Clarity, Spec §FR-013]
- [ ] CHK011 - Is the worker thread count for batch processing explicitly specified (default `3` workers)? [Clarity, Contracts §CLI Interfaces]

## 3. Requirement Consistency & Governance Alignment

- [ ] CHK012 - Does the `HIGH` fraud risk auto-REJECT override in `final_reporter_node` strictly enforce Constitution Principle I (Safety First)? [Consistency, Constitution §Principle I, Spec §FR-005]
- [ ] CHK013 - Do data extraction requirements enforce zero-hallucination policies by prohibiting invented figures and mandating `N/A` / `Data Missing` tags per Constitution Principle II? [Consistency, Constitution §Principle II, Spec §FR-002]
- [ ] CHK014 - Does the multi-agent graph layout adhere to fan-out / fan-in parallel execution guidelines per Constitution Principle III? [Consistency, Constitution §Principle III, Spec §FR-004]
- [ ] CHK015 - Do Thai text encoding specifications (`utf-8-sig`) align consistently across RSS news scraping, CSV export, and Streamlit table rendering per Constitution Principle IV? [Consistency, Constitution §Principle IV, Spec §FR-009, §FR-012]
- [ ] CHK016 - Do single-stock processing failure requirements align with batch resilience guidelines per Constitution Principle V? [Consistency, Constitution §Principle V, Spec §SC-006]

## 4. Acceptance Criteria & Measurability

- [ ] CHK017 - Can the 100% auto-REJECT rate for high accounting fraud risk stocks be objectively verified? [Measurability, Spec §SC-001]
- [ ] CHK018 - Can zero-hallucination metric parsing be tested programmatically against raw `yfinance` payloads? [Measurability, Spec §SC-002]
- [ ] CHK019 - Is the batch execution duration target (< 10 minutes for SET100 list) verifiable with performance benchmarks? [Measurability, Spec §SC-003]
- [ ] CHK020 - Can the notification dispatch latency (< 30 seconds post-evaluation) be objectively measured? [Measurability, Spec §SC-005]
- [ ] CHK021 - Is the CSV export file compatibility in Microsoft Excel (no mojibake) testable with automated decoding checks? [Measurability, Spec §SC-004]

## 5. Scenario & Edge Case Coverage

- [ ] CHK022 - Are requirements defined for tickers with missing financial fields or delisted state on `yfinance`? [Coverage, Spec §Edge Cases]
- [ ] CHK023 - Are requirements specified for RSS scraping when 0 news articles are returned for `{ticker} หุ้น` (fallback to neutral sentiment `0`)? [Coverage, Spec §Edge Cases]
- [ ] CHK024 - Are requirements documented for invalid or unconfigured Telegram / LINE bot tokens (graceful degradation without crashing)? [Coverage, Spec §Edge Cases]
- [ ] CHK025 - Are requirements specified for partial network timeouts during multi-worker batch scans (log and skip ticker)? [Coverage, Spec §Edge Cases, Quickstart §Scenario 4]
- [ ] CHK026 - Does the spec define user filter behavior in Streamlit when zero stocks match the filter criteria? [Coverage, Gap]

## 6. Non-Functional & System Operational Requirements

- [ ] CHK027 - Are rate-limiting sleep intervals specified between Google News RSS scraping calls during batch runs? [NFR, Research §R4]
- [ ] CHK028 - Are structured output schema constraints (`ge=0, le=100` for scores, `ge=-100, le=100` for sentiment) specified for Gemini Pydantic models? [NFR, Data Model §Schemas]
- [ ] CHK029 - Are requirements specified for Streamlit cache invalidation (`st.cache_data.clear()`) on manual refresh trigger? [NFR, Spec §FR-014]
- [ ] CHK030 - Are exit codes (0 for success, 1 for data error, 2 for API error) defined for CLI execution contracts? [NFR, Contracts §CLI Interfaces]

---

## Summary & Status

- **Total Checklist Items**: 30 (CHK001 – CHK030)
- **Traceability Rate**: 100% (All items reference Spec, Plan, Data Model, Contracts, or explicit Gaps)
- **Status**: Ready for pre-implementation requirements review.

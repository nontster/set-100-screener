# Feature Specification: SET100 AI Stock Screener & Anti-Fraud Suite

**Feature Branch**: `001-set100-stock-screener`

**Created**: 2026-07-25

**Status**: Verified

**Input**: User description: "Specifies the functional, non-functional, and technical architectural requirements for building the SET100 AI Stock Screener & Anti-Fraud Suite."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated SET100 Stock Screening & Anti-Fraud Override (Priority: P1)

As a financial analyst or individual investor, I want an automated screening engine to evaluate SET100 Thai stocks concurrently for financial quality, accounting risk, and news sentiment, so that any stock with high accounting risk is immediately flagged as REJECT regardless of valuation, and safe value candidates are scored and ranked using a combined quality-sentiment scoring formula.

**Why this priority**: Core value proposition. Financial safety overrides valuation; automated parallel analysis ensures high throughput and rigorous risk prevention.

**Independent Test**: Can be tested by running the screening workflow against a test batch of SET100 tickers (including known high-risk and high-quality stocks) and verifying that high-risk stocks are flagged as REJECT while safe value candidates receive PASS or WATCHLIST designations with correctly calculated total scores.

**Acceptance Scenarios**:

1. **Given** a Thai stock ticker symbol (e.g., "CPALL"), **When** the screening workflow executes, **Then** financial metrics are fetched directly from verified sources using proper `.BK` suffix mapping with 12-hour local caching to prevent rate limiting, without inventing numerical figures.
2. **Given** a stock with severe accounting discrepancies (e.g., Net Income vs CFO divergence or high debt coverage risk), **When** the Anti-Fraud evaluation completes, **Then** the final recommendation MUST be overridden to REJECT regardless of valuation score.
3. **Given** a stock with low accounting risk, a Value Score >= 70, and news sentiment score >= -20, **When** the final synthesis completes, **Then** the total score is computed as `Total Score = (Value Score * 0.7) + (((Sentiment Score + 100) / 2) * 0.3)` minus Fraud Risk penalty (`LOW` = 0, `MEDIUM` = -20), and the system outputs a PASS decision with an executive summary.
4. **Given** missing financial metrics for a ticker, **When** data extraction completes, **Then** missing fields are explicitly marked as `N/A` or `Data Missing` rather than hallucinated or assigned zero.

---

### User Story 2 - Multi-Channel Alerts & Batch Digest (Priority: P2)

As an active investor, I want to receive a consolidated batch digest notification after post-market scans, as well as instant single-stock alerts for manual dashboard screens via Telegram and LINE, so that I can stay updated on PASS candidates without manual tracking.

**Why this priority**: Enables timely decision-making by delivering high-conviction screening results directly to mobile/messaging channels.

**Independent Test**: Can be tested by triggering the notification engine with mock PASS results (both single and batch digest) and verifying successful receipt of formatted Markdown alerts on configured Telegram and LINE channels.

**Acceptance Scenarios**:

1. **Given** a completed 17:00 ICT daily post-market batch screening run, **When** the batch run finishes, **Then** a consolidated Batch Digest notification listing all PASS stocks is dispatched to Telegram and LINE.
2. **Given** a manual single-stock screening executed from the dashboard with recommendation `PASS`, **When** evaluation completes, **Then** an instant single-stock alert message containing key metrics, total score, and executive summary is dispatched to Telegram and LINE.
3. **Given** a stock screening result evaluated with recommendation `WATCHLIST` or `REJECT`, **When** the notification step executes, **Then** no single-stock alert is dispatched.

---

### User Story 3 - Interactive Web Dashboard & Stock Deep-Dive (Priority: P3)

As an analyst or investor, I want an interactive web dashboard to view summary metrics, filter screening reports, analyze visual scatter plots, and explore deep-dive stock insights (including live candlestick charts and AI executive summaries).

**Why this priority**: Provides visual exploration, interactive filtering, and detailed qualitative backing for investment decisions.

**Independent Test**: Can be tested by launching the web dashboard, applying filter sliders/multi-selects, verifying metric card updates, rendering Plotly distribution and scatter charts, and selecting a stock to view its deep-dive page and 1-year candlestick chart.

**Acceptance Scenarios**:

1. **Given** the dashboard home page, **When** viewed, **Then** summary cards display total stocks scanned, PASS count, WATCHLIST count, and REJECT count alongside an interactive filtering sidebar.
2. **Given** the screening result table, **When** filtering parameters (recommendation status, fraud risk level, minimum total score) are changed, **Then** table rows update dynamically with color-coded badges (Green for PASS, Yellow for WATCHLIST, Red for REJECT) and score progress bars.
3. **Given** the Stock Deep-Dive view, **When** a specific stock ticker is selected from the dropdown, **Then** the page displays the AI executive summary, valuation status, detailed red flags list, and an interactive 1-year candlestick price chart.

---

### User Story 4 - Automated Post-Market Daily Batch Processing & Export (Priority: P4)

As a system operator, I want the system to run an automated daily batch screening job across all SET100 stocks post-market close (17:00 ICT), handle network/API errors gracefully, and automatically export formatted Excel and UTF-8-SIG CSV reports.

**Why this priority**: Ensures hands-off daily operational updates and persistent report generation for external auditing and sharing.

**Independent Test**: Can be tested by triggering the batch pipeline for all SET100 tickers, verifying retry/fallback handling for simulated single-stock network failures, and confirming generated `.xlsx` and `.csv` files exist with valid Thai text formatting.

**Acceptance Scenarios**:

1. **Given** the scheduled time of 17:00 ICT on market trading days (Mon-Fri), **When** the scheduler triggers, **Then** the full SET100 batch screening workflow executes automatically.
2. **Given** a single stock encountering an API rate limit or network timeout, **When** processing occurs, **Then** the pipeline logs the error, skips or retries the failed ticker, and continues batch processing without crashing the entire pipeline.
3. **Given** a completed batch scan, **When** report export runs, **Then** `SET100_AI_Screening_Report.xlsx` and `SET100_AI_Screening_Report.csv` (encoded in `utf-8-sig` for proper Thai character display in Excel) are saved, sorted by Recommendation status and Total Score.

---

### Edge Cases

- **Missing/Delisted Financial Data**: Ticker suffix `.BK` returns empty financial statements or missing key metrics (e.g., missing CFO or P/E ratio). The system must handle missing attributes cleanly, mark missing values as `N/A` or `Data Missing`, and lower the overall confidence/score without crashing.
- **Thai News Scraper Rate Limiting or Zero News**: Scraper finds 0 news articles for `{ticker} หุ้น` query. System must set sentiment score to neutral default (`0`), log the absence of news, and allow downstream decision nodes to complete normally.
- **Severe Negative News Override**: Stock passes anti-fraud and valuation thresholds, but news sentiment score is below `-50` (severe reputational/legal news risk). System must override final decision from PASS to `WATCHLIST` or `REJECT`.
- **API Disconnection / Credentials Missing**: Invalid or missing Telegram/LINE API keys or Gemini API keys. System must log authorization errors gracefully, bypass push notifications if unconfigured, and allow batch/dashboard functionality to operate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept any Thai stock ticker symbol (e.g., "CPALL", "PTT") and append `.BK` suffix for fetching market and financial data.
- **FR-002**: System MUST parse financial metrics (P/E, P/BV, ROE, D/E Ratio, Free Cash Flow, Operating Cash Flow, Net Income, Dividend Yield, Current Ratio) strictly from verified data sources (`yfinance`). Missing data MUST be explicitly tagged as `N/A` or `Data Missing`.
- **FR-003**: System MUST implement local file-based data caching (12-hour TTL) for raw financial data to prevent hitting rate limits during repeated dashboard reloads and batch scans.
- **FR-004**: System MUST execute Anti-Fraud, Value Screener, and News Scraper/Sentiment evaluations in a parallel multi-agent graph workflow.
- **FR-005**: System MUST enforce an Anti-Fraud Override rule: Any stock assigned a `HIGH` Accounting Fraud Risk MUST be categorized as `REJECT` regardless of valuation or sentiment scores.
- **FR-006**: System MUST calculate Total Score using the formula `Total Score = (Value Score * 0.7) + (((Sentiment Score + 100) / 2) * 0.3) - Fraud Penalty`, where `Fraud Penalty` is `0` for LOW risk, `20` for MEDIUM risk, and triggers an auto-REJECT for HIGH risk.
- **FR-007**: System MUST assign a final recommendation of `PASS` ONLY when Fraud Risk is `LOW`, Value Score is >= 70, and Sentiment Score is >= -20.
- **FR-008**: System MUST override a potential `PASS` decision to `WATCHLIST` or `REJECT` whenever News Sentiment Score falls below `-50`.
- **FR-009**: System MUST scrape up to top 5 recent Thai news items for query `{ticker} หุ้น` using Google News RSS, preserving Thai text encoding (`utf-8-sig`).
- **FR-010**: System MUST dispatch a consolidated Batch Digest notification to Telegram and LINE upon completion of daily post-market batch runs, and instant single-stock alerts for manual single-ticker dashboard scans resulting in `PASS`.
- **FR-011**: System MUST process the SET100 ticker list in batch mode using rate-limited worker threads and display progress tracking.
- **FR-012**: System MUST export batch screening results to both Excel (`SET100_AI_Screening_Report.xlsx`) and UTF-8-SIG encoded CSV (`SET100_AI_Screening_Report.csv`).
- **FR-013**: System MUST schedule automated post-market daily batch runs at 17:00 ICT (Asia/Bangkok timezone) on trading days (Monday to Friday).
- **FR-014**: System MUST provide an interactive web dashboard with key summary metric cards, interactive filter controls, sortable tables with color-coded badges, Plotly distribution charts, and a stock deep-dive page with 1-year candlestick price charts.

### Key Entities *(include if feature involves data)*

- **StockState**: Unified workflow state holding ticker symbol, raw financial metrics, anti-fraud evaluation, value screening metrics, news items, sentiment analysis output, final decision recommendation, and total score.
- **FraudAnalysisSchema**: Structured model containing `fraud_risk_level` (LOW, MEDIUM, HIGH), `cash_flow_quality`, `red_flags` (list of strings), and `reasoning`.
- **ValueAnalysisSchema**: Structured model containing `is_value_stock` (boolean), `score` (0-100), `valuation_status` (UNDERVALUED, FAIRLY_VALUED, OVERVALUED), `key_strengths` (list), and `key_weaknesses` (list).
- **SentimentAnalysisSchema**: Structured model containing `overall_sentiment` (POSITIVE, NEUTRAL, NEGATIVE), `sentiment_score` (-100 to +100), `key_catalysts` (list), `key_risks` (list), and `news_summary`.
- **FinalDecisionSchema**: Structured model containing `recommendation` (PASS, WATCHLIST, REJECT), `total_score` (0-100), and `executive_summary`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of stocks with identified high accounting fraud risks (e.g., negative CFO with high net income) are automatically flagged as REJECT.
- **SC-002**: Zero financial metric hallucination: 100% of reported numerical metrics match raw source data or are explicitly marked `N/A` / `Data Missing`.
- **SC-003**: Full SET100 batch screening completes in under 10 minutes when using parallel worker execution.
- **SC-004**: 100% of generated CSV reports open seamlessly in Excel with legible Thai characters (via UTF-8-SIG BOM encoding).
- **SC-005**: 100% of PASS recommendations generate and deliver structured push notifications (digest or single-stock) within 30 seconds of execution completion.
- **SC-006**: Single-stock API or news scraping failures do not crash the batch job, yielding a 99.9%+ batch completion rate across valid SET100 tickers.

## Assumptions

- **Market Data Availability**: `yfinance` provides basic historical prices and financial statement items for Stock Exchange of Thailand tickers using the `.BK` suffix.
- **API Credentials**: Valid `GOOGLE_API_KEY` for Gemini LLM, as well as Telegram and LINE bot tokens/IDs, are configured in `.env`.
- **Timezone**: All scheduled jobs and time-sensitive operations follow ICT / `Asia/Bangkok` timezone.
- **Operating System & Environment**: System runs on Python 3.10+ in macOS/Linux environments with access to standard network endpoints for RSS and financial APIs.

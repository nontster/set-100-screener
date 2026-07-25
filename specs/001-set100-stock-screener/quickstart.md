# Quickstart: SET100 AI Stock Screener & Anti-Fraud Suite

**Date**: 2026-07-25 | **Plan**: [plan.md](./plan.md)

## Prerequisites

1. **Python 3.10+** installed
2. **API Keys** configured in `.env` at project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
   LINE_USER_ID=your_line_user_id
   ```
3. **Dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

```bash
# Clone and enter project
git clone <repo-url>
cd set-100-screener

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

## Validation Scenarios

### Scenario 1: Single Stock Screening (US1 - P1)

Validates the core LangGraph workflow end-to-end for a single ticker.

```bash
python -m src.graph --ticker CPALL
```

**Expected Output**:
- Financial metrics fetched (P/E, P/BV, ROE, etc.) — no `None` values without `N/A` labeling
- Fraud analysis with risk level (LOW/MEDIUM/HIGH)
- Value score (0-100) with valuation status
- News sentiment score (-100 to +100)
- Final recommendation (PASS/WATCHLIST/REJECT) with total score and executive summary

**Verify Anti-Fraud Override**: Run against a ticker known to have cash flow discrepancies. If `fraud_risk_level` is HIGH, recommendation MUST be REJECT regardless of value score.

---

### Scenario 2: Notification Dispatch (US2 - P2)

Validates Telegram and LINE alerts fire for PASS results.

```bash
python -m src.graph --ticker CPALL --notify
```

**Expected Output** (if PASS):
- Telegram message received in configured chat with Markdown-formatted alert
- LINE message received with stock summary
- If WATCHLIST/REJECT: no notification dispatched (verify no message sent)

**Verify Missing Credentials**: Remove `TELEGRAM_BOT_TOKEN` from `.env`. Re-run. System should log a warning and continue without crashing.

---

### Scenario 3: Streamlit Dashboard (US3 - P3)

Validates the web UI renders correctly with filtering and charts.

```bash
streamlit run src/app.py
```

**Expected Output** (browser opens at `http://localhost:8501`):
- Sidebar with "Run Screener" button, recommendation filter, fraud risk filter, score slider
- Summary cards showing Total Scanned, PASS, WATCHLIST, REJECT counts
- Tab 1: Interactive table with color-coded badges and score progress bars
- Tab 2: Plotly pie chart + scatter plot (Value Score vs Total Score, colored by Fraud Risk)
- Tab 3: Stock deep-dive with dropdown, AI summary, red flags, 1-year candlestick chart

---

### Scenario 4: Batch Processing & Export (US4 - P4)

Validates full SET100 batch run with report generation.

```bash
python -m src.batch
```

**Expected Output**:
- Progress bar (tqdm) tracking ~100 tickers
- Completed in under 10 minutes
- Generated files:
  - `SET100_AI_Screening_Report.xlsx` (Excel with formatted columns)
  - `SET100_AI_Screening_Report.csv` (UTF-8-SIG encoded)
- Open CSV in Excel → Thai characters display correctly (no mojibake)
- Results sorted by Recommendation (PASS first), then Total Score descending

**Verify Fault Tolerance**: Disconnect network briefly during batch run. System should log errors for affected tickers and continue processing remaining stocks.

---

### Scenario 5: Scheduler (US4 - P4)

Validates the automated daily trigger.

```bash
python -m src.scheduler
```

**Expected Output**:
- Scheduler starts and logs: "Scheduled batch screening at 17:00 ICT (Mon-Fri)"
- At 17:00 ICT on a weekday, batch screening automatically executes
- For testing: temporarily change trigger time to current time + 1 minute to verify firing

---

## Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires .env with valid API keys)
pytest tests/integration/ -v

# All tests
pytest -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `yfinance` returns empty data | Verify ticker exists: `yfinance.Ticker("CPALL.BK").info` |
| Thai characters garbled in CSV | Ensure CSV opened with UTF-8-SIG encoding; use `encoding='utf-8-sig'` |
| Telegram notification not received | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`; test with `curl` |
| LINE notification not received | Verify `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_USER_ID`; check LINE developer console |
| Gemini API error | Verify `GOOGLE_API_KEY` in `.env`; check quota at Google AI Studio |
| Scheduler not firing | Verify system timezone matches `Asia/Bangkok`; check APScheduler logs |

# Interface Contracts: SET100 AI Stock Screener & Anti-Fraud Suite

**Date**: 2026-07-25 | **Plan**: [plan.md](../plan.md)

## CLI Interfaces

### Single Stock Screening

```bash
python -m src.graph --ticker <TICKER> [--notify]
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--ticker` | `str` | Yes | Thai stock symbol without `.BK` suffix (e.g., `CPALL`, `PTT`) |
| `--notify` | flag | No | If present, dispatch Telegram/LINE alerts for PASS results |

**Output** (stdout, JSON):
```json
{
  "ticker": "CPALL",
  "recommendation": "PASS",
  "total_score": 78.5,
  "fraud_risk_level": "LOW",
  "value_score": 82,
  "sentiment_score": 45,
  "executive_summary": "..."
}
```

**Exit Codes**:
- `0`: Success
- `1`: Invalid ticker or data fetch failure
- `2`: Gemini API error

---

### Batch Screening

```bash
python -m src.batch [--workers <N>] [--output-dir <DIR>]
```

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--workers` | `int` | No | `3` | Number of concurrent ThreadPoolExecutor workers |
| `--output-dir` | `str` | No | `.` (cwd) | Directory for Excel/CSV report output |

**Output Files**:
- `SET100_AI_Screening_Report.xlsx`
- `SET100_AI_Screening_Report.csv` (UTF-8-SIG)

**Exit Codes**:
- `0`: All tickers processed successfully
- `1`: Partial failure (some tickers failed, logged to stderr)

---

### Scheduler

```bash
python -m src.scheduler
```

No arguments. Runs as a blocking process. Executes `src.batch` at 17:00 ICT Mon-Fri.

---

### Streamlit Dashboard

```bash
streamlit run src/app.py
```

No custom arguments. Standard Streamlit CLI. Serves at `http://localhost:8501`.

---

## Notification Message Contracts

### Telegram Single-Stock Alert

```markdown
🟢 *PASS: {ticker}*

*Total Score*: {total_score}/100
*Value Score*: {value_score}/100
*Fraud Risk*: {fraud_risk_level}
*Sentiment*: {sentiment_score} ({overall_sentiment})

📊 *Executive Summary*
{executive_summary}
```

### Telegram Batch Digest

```markdown
📋 *SET100 Daily Screening Report*
📅 {date} | ⏰ {time} ICT

🟢 *PASS Stocks ({count})*:
{for each PASS stock:}
• {ticker}: Score {total_score} | Value {value_score}
{end}

📊 Summary: {total_pass} PASS | {total_watchlist} WATCHLIST | {total_reject} REJECT
```

### LINE Message Format

Same content as Telegram but sent as plain text (LINE `text` message type). Markdown formatting stripped.

---

## External API Contracts

### Telegram Bot API

```
POST https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage
Content-Type: application/json

{
  "chat_id": "{TELEGRAM_CHAT_ID}",
  "text": "{formatted_message}",
  "parse_mode": "Markdown"
}
```

### LINE Messaging API

```
POST https://api.line.me/v2/bot/message/push
Content-Type: application/json
Authorization: Bearer {LINE_CHANNEL_ACCESS_TOKEN}

{
  "to": "{LINE_USER_ID}",
  "messages": [
    {
      "type": "text",
      "text": "{formatted_message}"
    }
  ]
}
```

### Google News RSS

```
GET https://news.google.com/rss/search?q={ticker}+หุ้น&hl=th&gl=TH&ceid=TH:th
```

Response: XML with `<item>` elements containing `<title>`, `<link>`, `<pubDate>`, `<source>`.

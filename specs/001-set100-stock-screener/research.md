# Research: SET100 AI Stock Screener & Anti-Fraud Suite

**Date**: 2026-07-25 | **Plan**: [plan.md](./plan.md)

## R1: yfinance Thai Stock Data Availability

**Decision**: Use `yfinance` with `.BK` suffix for SET100 tickers (e.g., `CPALL.BK`).

**Rationale**: `yfinance` supports Stock Exchange of Thailand via the `.BK` suffix. It provides `info` dict (P/E, P/BV, ROE, Dividend Yield, Current Ratio), `cashflow` statement (Free Cash Flow, Operating Cash Flow), and `financials` (Net Income). The `balance_sheet` provides total debt and equity for D/E Ratio calculation.

**Alternatives Considered**:
- SET Market API (official): Requires paid subscription and approval process. Not suitable for MVP.
- Web scraping SET.or.th directly: Fragile, TOS-restricted, difficult to maintain.

**Key Findings**:
- `yfinance.Ticker("CPALL.BK").info` returns Thai stock metadata and valuation ratios.
- `yfinance.Ticker("CPALL.BK").cashflow` returns cash flow statement with `Operating Cash Flow` and `Free Cash Flow` rows.
- `yfinance.Ticker("CPALL.BK").financials` returns income statement with `Net Income` row.
- Some fields may return `None` for less liquid SET100 stocks — must handle gracefully.
- Rate limiting: yfinance uses Yahoo Finance backend; no official rate limit published but empirically ~2000 requests/hour works without issues. A 12-hour file cache prevents repeated hits.

---

## R2: LangGraph Fan-Out / Fan-In Pattern

**Decision**: Use LangGraph `StateGraph` with conditional branching via `add_node` and parallel fan-out using list-based edge mapping.

**Rationale**: LangGraph natively supports fan-out/fan-in via `Send` API or by defining multiple edges from a single node. The `StateGraph` approach with `TypedDict` state allows typed, immutable state passing between nodes.

**Alternatives Considered**:
- LangChain sequential chains: No native parallelism; would serialize all evaluations.
- Raw `asyncio.gather`: Loses graph observability and state management benefits.
- CrewAI: Different agent framework; doesn't integrate with LangChain Google GenAI as tightly.

**Key Findings**:
- Use `graph.add_edge("fetch_data", ["anti_fraud", "value_screener", "scrape_news"])` for fan-out.
- Use join node (`final_reporter`) that waits for all branches to write their state keys.
- `scrape_news` → `news_sentiment` is a sequential sub-chain within the parallel branch.
- LangGraph handles state merging automatically when multiple branches write to different state keys.

---

## R3: Gemini Structured Output via LangChain

**Decision**: Use `langchain-google-genai` with `ChatGoogleGenerativeAI(model="gemini-2.0-flash").with_structured_output(PydanticSchema)`.

**Rationale**: The `with_structured_output` method forces Gemini to return JSON conforming to a Pydantic v2 model. This eliminates hallucinated free-form numbers and enforces typed fields (enums for risk levels, bounded integers for scores).

**Alternatives Considered**:
- Raw Gemini API with JSON mode: Works but requires manual parsing and validation.
- OpenAI function calling: Would require switching LLM provider.

**Key Findings**:
- `with_structured_output` accepts any Pydantic `BaseModel` subclass.
- Enum fields (e.g., `fraud_risk_level: Literal["LOW", "MEDIUM", "HIGH"]`) are enforced at schema level.
- Score fields should use `Field(ge=0, le=100)` for bounded validation.
- Sentiment score uses `Field(ge=-100, le=100)`.

---

## R4: Google News RSS Thai Feed Scraping

**Decision**: Scrape Google News RSS at `https://news.google.com/rss/search?q={ticker}+หุ้น&hl=th&gl=TH&ceid=TH:th` using `requests` + `beautifulsoup4` XML parser.

**Rationale**: Google News RSS provides a free, structured XML feed with Thai language support. No API key required. Returns title, link, publication date, and source for each article.

**Alternatives Considered**:
- Google News API (official): Discontinued / severely limited.
- NewsAPI.org: Paid for production; limited Thai language coverage.
- Direct web scraping of Thai financial news sites: Fragile, TOS issues.

**Key Findings**:
- RSS feed returns `<item>` elements with `<title>`, `<link>`, `<pubDate>`, `<source>`.
- Thai text in RSS is UTF-8 encoded; parse with `BeautifulSoup(content, "xml")`.
- Limit to top 5 items via slicing `items[:5]`.
- If zero items returned, set sentiment to neutral default (score=0).
- Google may rate-limit aggressive scraping; add 1-2 second delays between requests in batch mode.

---

## R5: Telegram Bot API & LINE Messaging API

**Decision**: Use `requests.post` for both Telegram `sendMessage` and LINE `push` APIs with Markdown formatting.

**Rationale**: Both APIs are simple HTTP POST endpoints. No SDK dependency needed — `requests` is already in the stack. Telegram supports Markdown natively; LINE supports Flex Messages for rich formatting.

**Alternatives Considered**:
- `python-telegram-bot` library: Adds unnecessary dependency for simple message dispatch.
- LINE SDK: Heavyweight for single push message use case.

**Key Findings**:
- Telegram: `POST https://api.telegram.org/bot{token}/sendMessage` with `chat_id`, `text`, `parse_mode=Markdown`.
- LINE: `POST https://api.line.me/v2/bot/message/push` with `Authorization: Bearer {token}`, body: `{"to": user_id, "messages": [{"type": "text", "text": msg}]}`.
- Both require tokens stored in `.env`.
- Graceful fallback: if token is missing/invalid, log warning and skip notification without crashing.

---

## R6: File-Based Data Cache Strategy

**Decision**: JSON file cache in `.cache/` directory with 12-hour TTL based on file modification timestamp.

**Rationale**: Simple, zero-dependency caching that persists across process restarts. Cache key is ticker symbol; cache file is `.cache/{ticker}.json`. Check `os.path.getmtime()` against current time minus 12 hours.

**Alternatives Considered**:
- `diskcache` library: Adds dependency for simple use case.
- `shelve` / `pickle`: Not human-readable; harder to debug.
- In-memory dict: Lost on restart; doesn't help with repeated Streamlit reloads.

**Key Findings**:
- Cache directory: `.cache/` at project root (gitignored).
- File naming: `.cache/CPALL.json`, `.cache/PTT.json`, etc.
- TTL check: `time.time() - os.path.getmtime(cache_file) < 43200` (12 hours in seconds).
- Cache stores raw `yfinance` extracted dict (metrics only, not full Ticker object).
- Cache miss → fetch from yfinance → write to cache → return data.

---

## R7: APScheduler Cron Configuration

**Decision**: Use `apscheduler.schedulers.blocking.BlockingScheduler` with `CronTrigger(day_of_week='mon-fri', hour=17, minute=0, timezone=pytz.timezone('Asia/Bangkok'))`.

**Rationale**: APScheduler is lightweight, pure Python, and supports cron expressions with timezone awareness. The `BlockingScheduler` is appropriate for a dedicated scheduler process.

**Alternatives Considered**:
- System crontab: Platform-dependent; harder to configure timezone.
- Celery Beat: Massively over-engineered for single scheduled task.

**Key Findings**:
- Run scheduler as separate process: `python -m src.scheduler`.
- Scheduler calls `run_batch_screening()` function from `src/batch.py`.
- Must not conflict with Streamlit process (separate entry points).

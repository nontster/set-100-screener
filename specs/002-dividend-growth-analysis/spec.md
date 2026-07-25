# Feature Specification: Dividend vs. Growth Stock Analysis & Classification

**Feature Branch**: `002-dividend-growth-analysis`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "I want to add feature to make further analysis which ticker is dividend stock and which one is growth stock (Option B: Hybrid quantitative + LLM rationale synthesis, with Growth stocks evaluated against World Mega Trends such as AI, Data Centers, EV/Renewables, and Health/Aging)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Stock Categorization with Mega Trend Intelligence (Priority: P1)

As an investor using the SET100 screener, I want the system to automatically evaluate each ticker for Dividend and Growth profiles—combining quantitative fundamentals with Global Mega Trend alignment (e.g., AI, Data Centers, Renewable Energy, Health/Aging)—so that I can discover both steady income stocks and high-potential growth trend beneficiaries.

**Why this priority**: Core value proposition. Financial history (CAGR) alone misses emerging growth stocks entering mega-trend expansion phases (e.g. data center construction, AI adoption in Thailand).

**Independent Test**: Can be tested by running the analysis pipeline on a sample set of SET100 tickers and confirming that each ticker receives a category classification, quantitative score breakdown, and identified Mega Trend alignment tags (if applicable).

**Acceptance Scenarios**:

1. **Given** financial metrics with high Dividend Yield (≥4.0%) and safe Payout Ratio (≤85%), **When** categorization runs, **Then** the system classifies the ticker as "Dividend Stock" with payout safety indicators.
2. **Given** a ticker with historical Revenue/EPS growth OR strong alignment with identified World Mega Trends (e.g., Data Center infrastructure provider, AI cloud enabler), **When** categorization runs, **Then** the system classifies the ticker as "Growth Stock" and highlights its relevant Mega Trend drivers.
3. **Given** a ticker exhibiting both strong dividend payout yield and high Mega Trend growth positioning (e.g., utility expanding into data center power or renewable energy), **When** categorization runs, **Then** the system classifies the ticker as "Hybrid Stock (Dividend + Mega Trend Growth)".
4. **Given** a stock flagged with high accounting risk or fraud override by Safety checks, **When** categorization runs, **Then** the system marks the category as "REJECTED (Risk)" regardless of dividend or mega trend alignment.

---

### User Story 2 - Filtering & Categorization Dashboard by Investment Style & Mega Trend (Priority: P2)

As a user viewing the screening results in the report or dashboard UI, I want to filter, group, and sort tickers by assigned category (Dividend, Growth, Hybrid, Neutral) and by Mega Trend tag (e.g., Data Center & AI, Renewable Energy, Healthcare), so that I can quickly target thematic investment strategies.

**Why this priority**: Enables actionable decision-making and thematic filtering across the SET100 universe.

**Independent Test**: Can be tested by applying the "Growth Stock" filter alongside "Data Center / AI" mega-trend tag in the dashboard and verifying matching subset results.

**Acceptance Scenarios**:

1. **Given** a dataset of screened SET100 tickers, **When** the user filters by "Growth Stock" and selects "AI & Data Center", **Then** only growth tickers aligned with AI & Data Center trends are displayed.
2. **Given** the summary dashboard, **When** viewing the category distribution, **Then** the system displays breakdown visual charts for Dividend vs. Growth vs. Hybrid and top Mega Trend exposures in the market.

---

### User Story 3 - Transparent Rationale & Mega Trend Catalyst Breakdown (Priority: P3)

As an analyst, I want to view a detailed breakdown for any ticker showing quantitative metrics (Yield, Payout Ratio, 3-Yr CAGR) alongside synthesized LLM investment rationales and identified Mega Trend catalysts, so that I can verify the logic behind the classification.

**Why this priority**: Provides full transparency, linking hard financial metrics with qualitative strategic positioning.

**Independent Test**: Can be tested by opening a ticker detail card and validating that all financial figures, safety indicators, and mega-trend catalyst notes are explicitly rendered without hallucination.

**Acceptance Scenarios**:

1. **Given** a categorized ticker, **When** viewing ticker details, **Then** the user sees a transparent breakdown table containing Dividend Yield, Payout Ratio, Revenue CAGR, EPS CAGR, identified World Mega Trends, and an LLM-synthesized executive rationale.
2. **Given** a ticker with missing historical dividend or growth data, **When** viewing details, **Then** missing fields are explicitly displayed as "Data Missing" rather than zero or hallucinated figures.

---

### Edge Cases

- What happens when a stock has weak historical CAGR but strong recent Mega Trend entry (e.g. new Data Center investment announcement)?
  - The system classifies it as "Emerging Growth (Mega Trend)" with a note on qualitative catalyst transition.
- What happens when a high-yield dividend stock operates in a declining legacy sector with negative Mega Trend exposure?
  - The system flags it as "Dividend Stock (Value Trap Warning)".
- What if a company has zero Mega Trend alignment and low growth/dividend metrics?
  - The system classifies it as "Neutral / Uncategorized".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate quantitative dividend metrics for each ticker, including Dividend Yield, Dividend Payout Ratio, and 3-Year Dividend Growth Rate.
- **FR-002**: System MUST calculate quantitative growth metrics for each ticker, including 3-Year Revenue CAGR, 3-Year EPS Growth Rate, and ROE.
- **FR-003**: System MUST analyze company business descriptions, sector exposure, and news catalysts to identify alignment with World Mega Trends (including AI & Data Centers, Cloud/Digital Infrastructure, EV & Renewable Energy, Healthcare & Aging Society, and Smart Logistics).
- **FR-004**: System MUST classify each non-rejected ticker into one of four primary categories: `Dividend Stock`, `Growth Stock`, `Hybrid Stock`, or `Neutral/Uncategorized`.
- **FR-005**: System MUST evaluate Growth Stock status using a composite of quantitative metrics (CAGR) AND qualitative Mega Trend alignment score.
- **FR-006**: System MUST utilize LLM structured output synthesis (`gemini-3.6-flash`) to generate a concise, factual executive rationale explaining the classification and highlighting specific Mega Trend catalysts.
- **FR-007**: System MUST strictly enforce Safety & Anti-Fraud principles: any ticker flagged with high accounting risk MUST be assigned `REJECTED (Accounting/Fraud Risk)` regardless of yield, growth, or mega trend alignment.
- **FR-008**: System MUST support filtering, sorting, and exporting results by category and Mega Trend tag in Streamlit UI, CSV, and Excel exports.

### Key Entities

- **StockClassification**: Represents the classification output for a single ticker.
  - `ticker`: String (e.g., "ADVANC.BK")
  - `category`: Enum (`Dividend Stock`, `Growth Stock`, `Hybrid Stock`, `Neutral`, `REJECTED`)
  - `dividend_score`: Numeric score (0-100)
  - `growth_score`: Numeric score (0-100)
  - `payout_safety_status`: Enum (`Safe`, `Caution`, `Unsafe`, `N/A`)
  - `mega_trends`: List of Strings (e.g., `["AI & Data Center", "Digital Infrastructure"]`)
  - `mega_trend_alignment_score`: Numeric score (0-100)
  - `rationale`: LLM-synthesized narrative summarizing quantitative findings & mega-trend catalysts.
  - `metrics_used`: Key-value map of exact verified metrics (Yield %, Revenue CAGR %, EPS CAGR %, Payout Ratio %).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of non-errored SET100 tickers in a screening run receive a deterministic category classification, assigned Mega Trend tags (if applicable), and an executive rationale.
- **SC-002**: Growth stock classification captures both historical financial growth (CAGR ≥ 10%) and emerging World Mega Trend alignment (e.g. AI & Data Centers) with 0% numerical hallucination.
- **SC-003**: UI filtering by stock category and Mega Trend tags responds in under 0.5 seconds.
- **SC-004**: Safety override is 100% enforced: 0% of high-risk/fraud-flagged stocks are recommended as Dividend or Growth investments.

## Assumptions

- Mega Trend analysis leverages verified company profiles, sector classifications, and recent Thai financial news collected by the news scraper node (`scrape_news.py`).
- Recognized World Mega Trend Taxonomy for SET100 includes:
  - `AI & Data Center Infrastructure` (cloud, telecom infrastructure, power utilities for AI data centers)
  - `EV & Renewable Energy` (solar, battery, EV ecosystem)
  - `Healthcare & Wellness / Aging Society` (hospitals, medical tourism)
  - `Digital Commerce & Logistics` (e-commerce, automated logistics)
- Default metric thresholds for SET (Thai market):
  - Dividend Stock baseline: Dividend Yield ≥ 4.0% AND Payout Ratio ≤ 85%.
  - Growth Stock baseline: 3-Year Revenue CAGR ≥ 10.0% OR 3-Year EPS CAGR ≥ 12.0% OR High Mega-Trend Alignment Score (≥ 75/100).
  - Hybrid baseline: Meets both Dividend and Growth criteria.

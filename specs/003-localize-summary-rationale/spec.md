# Feature Specification: Localized Summary & Classification Rationale

**Feature Branch**: `003-localize-summary-rationale`

**Created**: 2026-07-26

**Status**: Verified

**Input**: User description: "I want new feature to let user specify language in Executive Summary and Classification Rational via .env such as in Thai. 2. It would be great if you can formatted the message such as **REJECT** in BOLD"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Standardized Environment Language Configuration (Priority: P1)

As a financial analyst or system operator, I want to specify the output language for Executive Summaries and Classification Rationales using standard ISO language/locale codes in `.env` (e.g., `APP_LANGUAGE=th` or `SUMMARY_LANGUAGE=th_TH`) so that generated reports are rendered in my preferred language.

**Why this priority**: ISO 639-1 (`th`, `en`) and IETF BCP 47 (`th-TH`, `en-US`) are universal standards for language configuration across internationalized software systems.

**Independent Test**: Set `APP_LANGUAGE=th` in `.env`, run stock analysis, and verify that Executive Summaries and Classification Rationales are generated in natural Thai.

**Acceptance Scenarios**:

1. **Given** `.env` contains `APP_LANGUAGE=th` (or `th_TH`, `th-TH`, `Thai`), **When** stock analysis runs, **Then** Executive Summary and Classification Rationale are generated in Thai.
2. **Given** `.env` contains `APP_LANGUAGE=en` (or `en_US`, `en-US`, `English`), **When** stock analysis runs, **Then** Executive Summary and Classification Rationale are generated in English.

---

### User Story 2 - Bold Decision Formatting & Deterministic Post-Processing (Priority: P1)

As a report reviewer, I want key recommendation decision labels (e.g., **REJECT**, **BUY**, **HOLD**, **NEUTRAL**, **PASS**) to be strictly bolded in Markdown syntax (`**REJECT**`) across all generated summaries and rationales so that decision outcomes are instantly scannable.

**Why this priority**: Essential for risk visibility and decision clarity, fulfilling the safety-first evaluation principle.

**Independent Test**: Generate a stock evaluation report yielding a decision (e.g., REJECT) and verify that 100% of recommendation decision references in the text contain Markdown bold syntax (`**REJECT**`).

**Acceptance Scenarios**:

1. **Given** an evaluation resulting in REJECT, **When** narrative report is generated, **Then** decision keywords appear strictly in bold markdown (`**REJECT**`).
2. **Given** localized narrative output (e.g., Thai), **When** recommendation terms are generated, **Then** decision labels maintain bold markdown formatting (`**REJECT**`).

---

### User Story 3 - Default Fallback & ISO Normalization (Priority: P2)

As a system administrator, if no language variable is configured or if an invalid code is supplied, the system must normalize the configuration and gracefully fall back to English (`en`) without disrupting execution.

**Why this priority**: Guarantees system resilience, backward compatibility, and error prevention.

**Independent Test**: Remove language variable from `.env` or set `APP_LANGUAGE=invalid_code`, run analysis, and verify fallback to English with valid report generation.

**Acceptance Scenarios**:

1. **Given** `APP_LANGUAGE` is omitted from `.env`, **When** analysis executes, **Then** system defaults language setting to English (`en`).
2. **Given** an unparseable or unsupported language code, **When** analysis executes, **Then** system logs a warning and falls back to English (`en`).

---

### Edge Cases

- **Locale Code Variations**: Handling `th`, `th_TH`, `th-TH`, `TH`, `Thai` cleanly as Thai language input.
- **LLM Markdown Omission**: If the LLM omits markdown bold asterisks around decision keywords, a deterministic post-processing layer automatically wraps decision terms in `**...**`.
- **Financial Metric Integrity**: Preserving exact numerical metrics, currency abbreviations (`THB`), financial ratios, and stock tickers without corruption or translation distortion.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support standard ISO 639-1 language codes (e.g., `th`, `en`) and BCP 47 locale codes (e.g., `th-TH`, `en-US`) configured via `.env` (`APP_LANGUAGE` or `SUMMARY_LANGUAGE`).
- **FR-002**: System MUST generate Executive Summaries and Classification Rationales in the target language specified by the configured ISO code.
- **FR-003**: System MUST fall back to English (`en`) if the environment variable is missing, empty, or set to an unrecognized language code.
- **FR-004**: System MUST instruct LLMs and enforce via deterministic post-processing that all recommendation decision terms (**REJECT**, **PASS**, **BUY**, **HOLD**, **NEUTRAL**, **WATCHLIST**) are formatted in bold Markdown syntax (`**...**`).
- **FR-005**: System MUST preserve exact numerical data, currency units (`THB`), financial ratios, and ticker symbols accurately across all localized outputs.

### Key Entities *(include if feature involves data)*

- **Language Code Config**: ISO 639-1 / BCP 47 language code (`en`, `th`, `th-TH`, `en-US`).
- **Localized Executive Summary & Rationale**: Generated narrative report text with embedded bold decision tokens.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated Executive Summaries and Classification Rationales match the language specified by the ISO code in `.env`.
- **SC-002**: 100% of recommendation decision keywords in generated summaries are formatted with bold Markdown syntax (`**...**`).
- **SC-003**: Zero financial figures or stock tickers altered or corrupted due to language translation.

## Assumptions

- Preferred environment variable name is `APP_LANGUAGE` (with fallback support for `SUMMARY_LANGUAGE`), accepting standard ISO 639-1 codes (`th`, `en`) and BCP 47 locale codes (`th-TH`, `en-US`).
- English (`en`) is the default fallback language.
- Markdown bold syntax (`**TEXT**`) is supported across all downstream output channels (Streamlit UI, Telegram/LINE notifications, and exports).

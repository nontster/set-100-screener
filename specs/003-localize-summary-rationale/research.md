# Phase 0 Research: Localized Summary & Classification Rationale

## Decision 1: Environment Language Configuration & Locale Normalization

- **Decision**: Define `APP_LANGUAGE` as the primary environment variable in `.env` (with fallback support for `SUMMARY_LANGUAGE`), and implement an ISO 639-1 / BCP 47 locale normalizer.
- **Rationale**: ISO 639-1 (`th`, `en`) and IETF BCP 47 (`th-TH`, `en-US`) are universal internationalization standards. Flexible normalization accepts variations (`th`, `th-TH`, `th_TH`, `Thai`, `TH`) and resolves them cleanly to the target language string passed to prompt templates.
- **Alternatives Considered**:
  - *Hardcoding language names in English*: Less flexible and non-standard for developers used to ISO language codes.
  - *Multiple separate variables per node*: Unnecessary complexity; a central `APP_LANGUAGE` setting keeps configuration clean.

## Decision 2: LLM Prompt Parameterization for Target Language

- **Decision**: Update `final_reporter_node` in `src/nodes/final_reporter.py` to inject target language instructions into the Gemini LLM prompt template.
- **Rationale**: Instructing Gemini to output in the resolved target language (e.g. Thai or English) guarantees high-quality, natural narrative executive summaries while keeping financial metrics intact.
- **Alternatives Considered**:
  - *Post-generation machine translation*: Adds API latency, cost, and risks corrupting technical financial figures. Direct LLM generation in target language is faster and produces superior financial narratives.

## Decision 3: Deterministic Regex Post-Processing for Bold Decision Terms

- **Decision**: Implement a deterministic regex helper function `enforce_bold_decisions(text: str) -> str` that post-processes generated summaries to guarantee all decision terms (**REJECT**, **PASS**, **WATCHLIST**, **BUY**, **HOLD**, **NEUTRAL**) are formatted in bold Markdown (`**...**`).
- **Rationale**: LLMs can occasionally omit asterisks or formatting tokens. A deterministic regex filter guarantees 100% compliance with SC-002 without relying solely on LLM compliance.
- **Alternatives Considered**:
  - *Relying only on LLM prompt instructions*: Subject to subtle LLM formatting non-determinism.

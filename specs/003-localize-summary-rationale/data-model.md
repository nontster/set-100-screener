# Data Model & Schema Modifications: Localized Summary & Classification Rationale

## Key Entities & Configuration Data Structures

### 1. Language Configuration Schema (`src/config.py`)

- **Attributes**:
  - `APP_LANGUAGE`: `Optional[str]` (reads `os.getenv("APP_LANGUAGE")` or `os.getenv("SUMMARY_LANGUAGE")`)
- **Normalized Output**:
  - `get_app_language() -> str`: Returns normalized language code (`"th"` or `"en"`), defaulting to `"en"`.
- **Supported ISO Code Mappings**:
  - Thai: `{"th", "th_th", "th-th", "thai"}` -> `"th"`
  - English: `{"en", "en_us", "en-us", "english"}` -> `"en"`
  - Default Fallback: Any unrecognized input -> `"en"`

### 2. Decision Formatting Post-Processor (`src/nodes/final_reporter.py`)

- **Decision Terms List**: `["REJECT", "PASS", "WATCHLIST", "BUY", "HOLD", "NEUTRAL", "HIGH FRAUD RISK"]`
- **Regex Rule**: Enforce `\b(TERM)\b` is converted to `**TERM**` (skipping terms already enclosed in `**...**`).

### 3. Final Decision State Schema (`src/schemas.py` / `src/state.py`)

- **Entity**: `FinalDecisionSchema`
- **Fields**:
  - `recommendation`: `str` (e.g. `"REJECT"`, `"PASS"`, `"WATCHLIST"`)
  - `total_score`: `float`
  - `executive_summary`: `str` (Localized narrative text containing bold decision tokens e.g. `**REJECT**`)

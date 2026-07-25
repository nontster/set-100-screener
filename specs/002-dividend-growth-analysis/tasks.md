# Tasks: Dividend vs. Growth Stock Analysis & Classification

**Input**: Design documents from `/specs/002-dividend-growth-analysis/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Shared data structures and schema definitions

- [ ] T001 Update Pydantic schemas in `src/schemas.py` with `StockClassificationSchema`, `StockCategory`, and `PayoutSafetyStatus`
- [ ] T002 Extend central `GraphState` in `src/state.py` with `classification_analysis` key

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core calculation and taxonomy helper logic

**⚠️ CRITICAL**: Must be complete before user story nodes execute

- [ ] T003 Implement quantitative metrics calculator (Yield %, Payout Ratio %, 3-Yr Revenue CAGR, 3-Yr EPS CAGR) in `src/nodes/stock_classifier.py`
- [ ] T004 Implement Mega Trend taxonomy evaluator (AI & Data Center, EV & Renewables, Healthcare, Logistics) in `src/nodes/stock_classifier.py`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Automatic Stock Categorization & Mega Trend Intelligence (Priority: P1) 🎯 MVP

**Goal**: Automatically classify SET100 tickers into Dividend, Growth, Hybrid, Neutral, or REJECTED categories using quantitative rules, Mega Trend tags, and LLM rationale synthesis.

**Independent Test**: Run unit/CLI analysis on sample SET tickers (e.g. ADVANC.BK) and verify `classification_analysis` schema and safety overrides.

### Implementation & Tests for User Story 1

- [ ] T005 [P] [US1] Write unit tests for stock classification rules and anti-fraud safety override in `tests/unit/test_stock_classifier.py`
- [ ] T006 [US1] Implement complete `stock_classifier_node` with Gemini LLM structured output synthesis in `src/nodes/stock_classifier.py`
- [ ] T007 [US1] Register `stock_classifier` node into LangGraph execution graph in `src/graph.py`

**Checkpoint**: User Story 1 is complete and independently testable via CLI and pytest

---

## Phase 4: User Story 2 - Filtering & Categorization Dashboard by Investment Style & Mega Trend (Priority: P2)

**Goal**: Allow filtering, sorting, and exporting screening results by stock category and Mega Trend tags in UI and CSV/Excel exports.

**Independent Test**: Filter screening table by "Growth Stock" and "AI & Data Center" in Streamlit dashboard and verify correct subset filtering and export generation.

### Implementation for User Story 2

- [ ] T008 [P] [US2] Update CSV and Excel export builders in `src/batch.py` and `src/nodes/final_reporter.py` to include classification columns
- [ ] T009 [US2] Add Stock Category selectbox and Mega Trend multiselect filters in `src/app.py`

**Checkpoint**: User Stories 1 AND 2 are functional and verifiable in Streamlit UI and exports

---

## Phase 5: User Story 3 - Transparent Rationale & Mega Trend Catalyst Breakdown (Priority: P3)

**Goal**: Display a detailed ticker breakdown view showing quantitative metrics, payout safety indicators, Mega Trend tags, and executive rationale notes.

**Independent Test**: Click ticker detail view in Streamlit and verify metric breakdown table displays without missing figures or errors.

### Implementation for User Story 3

- [ ] T010 [P] [US3] Add detailed Classification Breakdown expander card with metrics table and Mega Trend catalysts in `src/app.py`

**Checkpoint**: All user stories are complete and independently verifiable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and integration checks

- [ ] T011 [P] Implement end-to-end integration test for full screening pipeline with stock classifier in `tests/integration/test_classification_pipeline.py`
- [ ] T012 Run quickstart validation scenarios from `specs/002-dividend-growth-analysis/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS User Story 1
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 3 completion
- **User Story 3 (Phase 5)**: Depends on Phase 3 completion
- **Polish (Phase 6)**: Depends on Phase 3-5 completion

### Parallel Opportunities

- T001 and T002 can run sequentially or in parallel.
- T005 [US1] (unit test) can be written in parallel with T003/T004 before T006 implementation.
- T008 [US2] (export formatting) can run in parallel with T009 [US2] (UI filters).
- T010 [US3] (detail view) can be developed independently after Phase 3.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004)
3. Complete Phase 3: User Story 1 (T005, T006, T007)
4. **STOP and VALIDATE**: Run `python -m src.graph ADVANC.BK` and `pytest tests/unit/test_stock_classifier.py`
5. Proceed to Phase 4 (UI & Exports) once MVP passes verification.

# Tasks: Localized Summary & Classification Rationale

**Input**: Design documents from `/specs/003-localize-summary-rationale/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to User Story 1 (US1), User Story 2 (US2), or User Story 3 (US3) from spec.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify feature directory structure and setup environment requirements.

- [x] T001 Verify project structure and configuration keys per implementation plan

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core environment configuration helpers in `Config` required by all user stories.

**⚠️ CRITICAL**: Must be completed before node-level localization can begin.

- [x] T002 Add `APP_LANGUAGE` environment variable loader and `get_app_language()` locale normalizer method in `src/config.py`
- [x] T003 [P] Create unit test suite for ISO language code resolution and default fallback in `tests/unit/test_config_language.py`

**Checkpoint**: Foundation ready - language resolution helper available for LLM synthesis node.

---

## Phase 3: User Story 1 - Standardized Environment Language Configuration (Priority: P1) 🎯 MVP

**Goal**: Parameterize Gemini LLM summary prompt in `final_reporter_node` with target language instructions derived from `APP_LANGUAGE`.

**Independent Test**: Set `APP_LANGUAGE=th` in `.env` and verify `final_reporter_node` generates summary text in Thai.

### Implementation for User Story 1

- [x] T004 [US1] Inject `APP_LANGUAGE` target language instruction into Gemini LLM prompt in `src/nodes/final_reporter.py`
- [x] T005 [P] [US1] Add unit test for localized executive summary generation in `tests/unit/test_final_reporter_localization.py`

**Checkpoint**: At this point, User Story 1 is functional and generates summaries in the configured language.

---

## Phase 4: User Story 2 - Bold Decision Formatting & Deterministic Post-Processing (Priority: P1)

**Goal**: Implement `enforce_bold_decisions` regex helper to post-process summary output and strictly wrap recommendation keywords (**REJECT**, **PASS**, **WATCHLIST**, **BUY**, **HOLD**, **NEUTRAL**) in Markdown bold (`**...**`).

**Independent Test**: Run `enforce_bold_decisions` on narrative text with unbolded decision words and verify 100% of decision terms are converted to bold Markdown syntax (`**REJECT**`).

### Implementation for User Story 2

- [x] T006 [P] [US2] Create unit test suite for bold decision regex post-processor in `tests/unit/test_bold_formatting.py`
- [x] T007 [US2] Implement `enforce_bold_decisions(text: str) -> str` post-processing function in `src/nodes/final_reporter.py`
- [x] T008 [US2] Apply `enforce_bold_decisions` post-processor to `executive_summary` output in `src/nodes/final_reporter.py`

**Checkpoint**: User Story 2 guarantees 100% bold Markdown decision formatting across all summary outputs.

---

## Phase 5: User Story 3 - Default Fallback & ISO Normalization (Priority: P2)

**Goal**: Ensure invalid, missing, or unparseable language inputs default cleanly to English (`en`) without interrupting analysis pipeline or corrupting numerical metrics.

**Independent Test**: Omit `APP_LANGUAGE` or set `APP_LANGUAGE=invalid_code` and verify system defaults to English without error.

### Implementation for User Story 3

- [x] T009 [P] [US3] Add fallback and edge-case test scenarios (`invalid_lang`, missing `.env` key, uppercase `TH_TH`) in `tests/unit/test_config_language.py`
- [x] T010 [US3] Add numerical metric and currency (`THB`) preservation tests in `tests/unit/test_bold_formatting.py`

**Checkpoint**: All user stories functional, robust, and edge-case safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates and end-to-end validation.

- [x] T011 [P] Add `APP_LANGUAGE` configuration guide and `.env` examples to `README.md`
- [x] T012 Execute full test suite via `pytest` and validate scenarios in `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all User Stories.
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2).
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2); can run in parallel with US1.
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) and US1/US2.
- **Polish (Phase 6)**: Depends on completion of User Stories 1-3.

### Parallel Opportunities

- T003 [P] (`test_config_language.py`) can be created in parallel with T002 (`src/config.py`).
- T005 [P] (`test_final_reporter_localization.py`) can be developed in parallel with T004.
- T006 [P] (`test_bold_formatting.py`) can be written in parallel with T007.
- T011 [P] (`README.md`) can run in parallel with polish checks.

---

## Implementation Strategy (MVP First)

1. Complete Phase 1 & Phase 2 (Setup & Foundational `Config` updates).
2. Complete Phase 3 (User Story 1 - Prompt Parameterization).
3. Complete Phase 4 (User Story 2 - Bold Decision Regex Post-Processing).
4. Run validation via `pytest` to confirm MVP completion.

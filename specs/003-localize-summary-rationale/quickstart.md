# Quickstart & Validation Guide: Localized Summary & Bold Decisions

## Runnable Validation Commands

### 1. Test Unit Configuration Normalization
Run pytest on unit tests to verify ISO language code normalization and fallback behavior:
```bash
pytest tests/unit/test_config_language.py -v
```

### 2. Test Bold Decision Formatting Helper
Run unit tests verifying that `enforce_bold_decisions` wraps decision keywords cleanly:
```bash
pytest tests/unit/test_bold_formatting.py -v
```

### 3. Manual E2E Validation with `.env` Configuration

#### Thai Output Test:
1. Set `APP_LANGUAGE=th` in `.env`:
   ```bash
   echo "APP_LANGUAGE=th" >> .env
   ```
2. Run single stock evaluation CLI:
   ```bash
   python -m src.app --ticker EA.BK
   ```
3. Inspect `executive_summary` output in console/logs:
   - Verify narrative text is in Thai.
   - Verify recommendation status is bolded (e.g. `**REJECT**`).
   - Verify numerical financial figures remain exact.

#### English Default Fallback Test:
1. Remove `APP_LANGUAGE` from `.env` or set `APP_LANGUAGE=en`.
2. Run single stock evaluation CLI:
   ```bash
   python -m src.app --ticker EA.BK
   ```
3. Verify narrative text is in English with bolded recommendation status (`**REJECT**`).

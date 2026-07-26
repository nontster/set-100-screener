# Interface Contract: Language Configuration & Decision Formatting

## 1. Environment Variable Contract

| Environment Variable | Allowed Values | Default Fallback | Description |
| :--- | :--- | :--- | :--- |
| `APP_LANGUAGE` | `th`, `th-TH`, `en`, `en-US`, `Thai`, `English` | `en` | Primary language config for generated Executive Summary & Rationale |
| `SUMMARY_LANGUAGE` | Same as above | Fallback if `APP_LANGUAGE` unset | Secondary/legacy variable alias |

## 2. Config Method API Contract (`Config`)

```python
class Config:
    @classmethod
    def get_app_language(cls) -> str:
        """
        Returns normalized language string: 'th' or 'en'.
        Defaults to 'en' if unset or invalid.
        """
        ...
```

## 3. Decision Formatting Contract (`final_reporter.py`)

```python
def enforce_bold_decisions(text: str) -> str:
    """
    Ensures recommendation decision keywords in text are wrapped in markdown bold (**KEYWORD**).
    Example input: "We issue a definitive REJECT recommendation..."
    Example output: "We issue a definitive **REJECT** recommendation..."
    """
    ...
```

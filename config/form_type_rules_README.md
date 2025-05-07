# Form Type Rules Guide – Safe Harbor EDGAR AI

This configuration file categorizes SEC `form_type` values by their relevance to investment signal analysis. 

## Integration Summary

- `core_registration_forms`: Always included in ingestion and filtering logic

Use in your orchestrators via `load_form_type_rules()` from `config_loader.py`. Do not add metadata fields like `priority` or `category` here — reserve those for `form_priority.yaml` or UI logic.

## Categories

### ✅ core_registration_forms
Includes IPOs, secondary offerings, stock-based compensation registrations, and deal-related filings.
Used to detect:
- IPO terms (e.g. S-1, F-1, 424B1)
- Follow-on or shelf offerings (e.g. S-3, F-3)
- Stock issuance (S-8)
- M&A, SPAC-related votes or disclosures (425, S-4)
- Exchange listings (8-A12B)

## Integration Notes

Load this config using `config_loader.py` in your pipeline and apply allow/block logic in orchestrators and parsers.

---

## Usage in Python Code:

```python
from utils.config_loader import load_form_type_rules

rules = load_form_type_rules("config/form_type_rules.yaml")

def is_allowed(form_type: str, include_optional: bool = False) -> bool:
    if form_type in rules["exclude_forms"]:
        return False
    if form_type in rules["core_registration_forms"]:
        return True
    if include_optional and form_type in rules["optional_forms"]:
        return True
    return False
```
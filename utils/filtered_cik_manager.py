import json

# Enhance later with `company_tickers.json` to map `ticker` -> `cik` and `market_data.py` for dynamic `ticker` filtering.

class FilteredCikManager:
    def __init__(self, cik_allowlist_path: str, allowed_form_types: list[str]):
        with open(cik_allowlist_path, "r") as f:
            self.allowed_ciks = set(json.load(f))
        self.allowed_form_types = set(allowed_form_types)

    def is_allowed(self, cik: str, form_type: str) -> bool:
        return cik in self.allowed_ciks and form_type in self.allowed_form_types

    def filter(self, records: list[dict]) -> list[dict]:
        return [
            rec for rec in records
            if self.is_allowed(rec["cik"], rec["form_type"])
        ]

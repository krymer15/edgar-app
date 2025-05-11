# Mapping filings to fiscal periods

Rather than baking fiscal-period codes into the folder structure, it’s more flexible to:

1. Enrich your metadata model (in Postgres/ORM) with:
- `fiscal_year` (e.g. 2024)
- `fiscal_quarter` or `period_end` (e.g. “Q4” or `2024-12-31`)

2. Query/filter at runtime:

```python
# pseudo-code example
docs = session.query(FilingDocument)\
              .filter(FilingDocument.cik == target_cik)\
              .filter(FilingDocument.fiscal_year == 2024)\
              .filter(FilingDocument.fiscal_quarter == "Q4")\
              .all()
for d in docs:
    path = path_manager.build_parsed_path(d.cik, d.accession, base_dir="/data/parsed")
    …
```

Any change in how you calculate periods (e.g., non-calendar year ends) is easier to adjust in code/DB than in a rigid folder hierarchy.


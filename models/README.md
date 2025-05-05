# models/

This folder defines all SQLAlchemy ORM models for Postgres tables used in the EDGAR AI Platform.

## Philosophy

We enforce a normalized, low-redundancy schema:
- Foreign keys link tables via accession_number
- No duplication of cik, form_type, or URL
- Derived fields (like full URLs) are rebuilt dynamically when needed

## xml_metadata

Tracks XML files discovered during ingestion (Forms 3, 4, 5, 10-K).

| Column             | Type    | Notes                            |
|--------------------|---------|----------------------------------|
| id                 | UUID    | Primary key                      |
| accession_number   | TEXT    | FK to daily_index_metadata       |
| filename           | TEXT    | Just the filename (e.g. `doc4.xml`) |
| downloaded         | BOOL    | Was the XML downloaded?          |
| parsed_successfully| BOOL    | Was the file parsed?             |
| created_at         | TIMESTAMP | Auto-generated on insert        |
| updated_at         | TIMESTAMP | Auto-updated on modification    |

Use `utils/url_builder.py` to dynamically generate download URLs:

```python
from utils.url_builder import construct_primary_document_url
url = construct_primary_document_url(cik, accession_number, filename)
```
# models/

Contains all data definitions for the EDGAR pipeline.

- **dataclasses/**  
  Pure `@dataclass` objects used internally by downloaders, parsers, and extractors.
- **orm_models/**  
  SQLAlchemy ORM models mapping to your Postgres schema.
- **adapters/**  
  Conversion utilities between dataclasses and ORM models (both directions).

## Data Flows among Models:

### `sgml`:

```markdown
SGML content (`.txt`)
   ↓
`SgmlDocumentIndexer` → [FilingDocumentMetadata]
   ↓ adapter
`convert_parsed_doc_to_filing_doc()`
   ↓
`FilingDocumentRecord` (cleaned dataclass)
   ↓ writer
`convert_filing_doc_to_orm()`
   ↓
`FilingDocument` (SQLAlchemy ORM model)
   ↓
Postgres
```

## Reverse Mapping: `orm_to_dataclass()`
Your orchestrators shouldn’t import SQLAlchemy models directly. Instead, provide adapter functions:

```python
# models/adapters/orm_to_dataclass.py

def metadata_to_header(meta: FilingMetadata) -> FilingHeader:
    return FilingHeader(
        accession_number=meta.accession_number,
        form_type=meta.form_type,
        filing_date=meta.filing_date,
        report_date getattr(meta, "report_date", None),
    )

def document_model_to_raw(doc_model: FilingDocument) -> RawDocument:
    return RawDocument(
        accession_number=doc_model.accession_number,
        cik=doc_model.cik,
        form_type=doc_model.filing.form_type,
        filename=doc_model.filename,
        source_url=doc_model.source_url,
        doc_type=doc_model.source_type,
        source_type=doc_model.source_type,
        is_primary=doc_model.is_primary,
        is_exhibit=doc_model.is_exhibit,
        accessible=doc_model.accessible,
    )
```

- Use these in your downloaders or parsers when bootstrapping from existing DB rows.
- Keeps SQLAlchemy out of your business logic.

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
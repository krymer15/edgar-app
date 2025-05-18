# Crawler IDX Writers

This folder contains writer modules responsible for persisting structured data extracted from `crawler.idx` and related SEC filings into the Postgres database.

These writers form the **final stage** of crawler.idx-based pipelines and are invoked by orchestrators to upsert parsed records.

## Components

### `FilingMetadataWriter`

Writes filing metadata records extracted from the daily `crawler.idx` file to the database.

- **Pipeline**: `Pipeline 1 – Filing Metadata Ingestion`
- **Input**: `List[FilingMetadata]` (dataclass pointer objects)
- **Output**: Records written to the `filing_metadata` table
- **Behavior**:
  - Uses `session.merge()` for upsert operations on records
  - Commits each record individually for better error isolation
  - Logs successful writes and failures
  - Returns count of successfully written records

```python
def upsert_many(self, records: list[FilingMetadataDC]):
    written = 0
    for record in records:
        try:
            orm_entry = convert_to_orm(record)
            self.session.merge(orm_entry)
            self.session.commit()
            written += 1
        except SQLAlchemyError as e:
            self.session.rollback()
            log_warn(f"[ERROR] Failed to write filing metadata for {record.accession_number}: {e}")
            
    log_info(f"✅ Metadata written: {written}")
```

### `FilingDocumentsWriter`

Writes document metadata records extracted from SEC filings to the database. This class extends the `BaseWriter` interface.

- **Pipeline**: Supports both document extraction pipelines
- **Input**: `List[FilingDocumentRecord]` (dataclass records)
- **Output**: Records written to the `filing_documents` table
- **Behavior**:
  - Performs deduplication checks based on accession_number, document_type, and source_url
  - Updates existing records if certain fields have changed (description, accessible, issuer_cik)
  - Adds new records for documents not previously seen
  - Uses a batched transaction approach with a single commit for all records
  - Provides detailed logging of written, updated, and skipped records

```python
def write_documents(self, documents: list[FilingDocDC]):
    written = 0
    updated = 0
    skipped = 0

    for dc in documents:
        try:
            # Deduplication check
            existing = self.db_session.query(FilingDocumentORM).filter_by(
                accession_number=dc.accession_number,
                document_type=dc.document_type,
                source_url=dc.source_url
            ).first()

            if existing:
                # Update if something changed
                updated_fields = False
                # Check each field that might be updated...
                if updated_fields:
                    updated += 1
                else:
                    skipped += 1
                continue

            new_doc = convert_filing_doc_to_orm(dc)
            self.db_session.add(new_doc)
            written += 1

        except SQLAlchemyError as e:
            self.db_session.rollback()
            log_error(f"DB error processing document {dc.filename or dc.source_url}: {e}")
            continue

    # Single commit for all changes
    try:
        self.db_session.commit()
    except SQLAlchemyError as e:
        self.db_session.rollback()
        log_error(f"Final commit failed: {e}")

    log_info(f"📝 Filing documents — Written: {written}, Updated: {updated}, Skipped: {skipped}")
```

## Database Schema

### Filing Metadata Table (`filing_metadata`)

Stores basic information about each filing in EDGAR:

- **Primary Key**: `accession_number`
- **Key Fields**:
  - `accession_number`: Unique identifier for the SEC filing
  - `cik`: Central Index Key of the filing entity
  - `form_type`: Type of SEC form (e.g., "10-K", "8-K", "4")
  - `filing_date`: Date the filing was submitted
  - `filing_url`: URL to access the filing on the SEC website
  - `processing_status`: Status flag for pipeline processing (added by migration)

### Filing Documents Table (`filing_documents`)

Stores metadata for each document within a filing:

- **Primary Key**: `id` (UUID)
- **Foreign Key**: `accession_number` references `filing_metadata(accession_number)`
- **Key Fields**:
  - `accession_number`: Links to the parent filing
  - `cik`: CIK of the filing entity
  - `document_type`: Type of document (e.g., "EX-10.1", "XML", "GRAPHIC")
  - `filename`: Original filename from SGML
  - `source_url`: URL to access the document
  - `is_primary`: Flag for primary document in filing
  - `is_exhibit`: Flag for exhibit documents
  - `accessible`: Flag indicating if the document is text-accessible
  - `issuer_cik`: CIK of the issuer (may differ from filing entity)

## Dataclass to ORM Conversion

Both writers rely on adapter functions from `models/adapters/dataclass_to_orm.py` to convert between dataclasses and ORM models:

- `convert_to_orm()`: Converts `FilingMetadataDC` to `FilingMetadataORM`
- `convert_filing_doc_to_orm()`: Converts `FilingDocumentRecord` to `FilingDocumentORM`

## Design Notes

- Writers are intentionally thin and only responsible for DB logic.
- `FilingMetadataWriter` commits each record individually for better error isolation.
- `FilingDocumentsWriter` uses a batched approach with a single commit for better performance.
- Deduplication and field update checks are performed within the writer to minimize database operations.
- Both writers implement extensive logging for tracking success and failure.

## Related Modules

| Component Type | Filing Metadata Pipeline | Filing Documents Pipeline |
|----------------|--------------------------|---------------------------|
| Collector      | `collectors/crawler_idx/filing_metadata_collector.py` | `collectors/crawler_idx/filing_documents_collector.py` |
| Parser/Indexer | `parsers/idx/idx_parser.py` | `parsers/sgml/indexers/sgml_document_indexer.py` |
| Dataclass      | `models/dataclasses/filing_metadata.py` | `models/dataclasses/filing_document_record.py` |
| ORM Model      | `models/orm_models/filing_metadata.py` | `models/orm_models/filing_document_orm.py` |
| Adapter        | `models/adapters/dataclass_to_orm.py:convert_to_orm()` | `models/adapters/dataclass_to_orm.py:convert_filing_doc_to_orm()` |
| Orchestrator   | `orchestrators/crawler_idx/filing_metadata_orchestrator.py` | `orchestrators/crawler_idx/filing_documents_orchestrator.py` |
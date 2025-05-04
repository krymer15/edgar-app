# Writers

This folder contains modules that write parsed results into Postgres.

## Key Classes

### `ParsedSgmlWriter`
- Writes:
  - Parsed filing metadata (`parsed_sgml_metadata`)
  - Exhibit rows (`exhibit_metadata`)
- Performs deduplication to avoid repeated inserts.

### `SgmlDocWriter`
- (Deprecated in favor of ParsedSgmlWriter)
- Wrote raw documents in earlier pipeline versions.

### `DailyIndexWriter`
- Stores crawler.idx metadata (optional archival use)

## Notes
- All writers use SQLAlchemy ORM.
- Canonical field for primary doc URL is `primary_doc_url`.
- `run_id` is recorded for traceability in logs and DB.

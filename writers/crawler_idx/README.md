# Crawler IDX Writers

This folder contains writer modules responsible for persisting structured data extracted from `crawler.idx` and related SEC filings into the Postgres database.

These writers form the **final stage** of crawler.idx-based pipelines and are invoked by orchestrators to upsert parsed records.

---

## 📌 Current Writers

### ✅ `FilingMetadataWriter`

- **Pipeline**: `Pipeline 1 – Filing Metadata Ingestion`
- **Input**: `List[FilingMetadata]` (dataclass pointer objects)
- **Output**: Upserts into the `filing_metadata` table
- **Behavior**:
  - Uses `session.merge()` for upserts
  - Commits all records in a single transaction
  - Rolls back on failure and logs the error

#### Method

```python
def upsert_many(self, records: list[FilingMetadata]):
    ...
```

## Design Notes
- Writers are intentionally thin and only responsible for DB logic.
- Conversion from `FilingMetadata` dataclass → ORM is handled by:

```python
from models.adapters.dataclass_to_orm import convert_to_orm
```

- If additional pre-validation is needed (e.g. deduplication, normalization), consider wrapping logic in the orchestrator or adding a pre-processor module.

## Future Enhancements
- Add run-level logging metadata (e.g. ingestion timestamps, run_id)
- Implement batch insert optimization for large index days
- Add writer hooks for test environments (e.g. SQLite fallback)

## Related Modules

| Stage        | Module Path                                                 |
| ------------ | ----------------------------------------------------------- |
| Collector    | `collectors/crawler_idx/filing_metadata_collector.py`       |
| Parser       | `parsers/idx/idx_parser.py`                                 |
| Dataclass    | `models/dataclasses/filing_metadata.py`                     |
| Orchestrator | `orchestrators/crawler_idx/filing_metadata_orchestrator.py` |

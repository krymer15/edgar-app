# Crawler IDX Orchestrators

This folder contains orchestrators that manage data flows based on the SEC's daily index feed (`crawler.idx`). These orchestrators are responsible for coordinating collectors, writers, and optional filters for metadata and filing document ingestion.

---

## Pipeline 1 – Filing Metadata Ingestion

### ✅ Orchestrator: `FilingMetadataOrchestrator`

This is the controlling unit for **Pipeline 1**, responsible for:
- Downloading the `crawler.idx` file
- Parsing it into `FilingMetadata` records
- Writing the metadata into the `filing_metadata` table in Postgres

### ⚙️ Flow Diagram

```text
             ┌────────────────────────────┐
             │  FilingMetadataOrchestrator│
             └────────────┬───────────────┘
                          │
        ┌─────────────────▼────────────────────────────┐
        │ FilingMetadataCollector (downloads, parses)  │
        └─────────────────┬────────────────────────────┘
                          │
         ┌────────────────▼─────────────────────┐
         │   FilingMetadataWriter (DB upsert)   │
         └──────────────────────────────────────┘
```

### CLI Runner
- Located at: `scripts/crawler_idx/run_daily_metadata_ingest.py`
- Supports:
    - `--date`: single-date mode
    - `--backfill N`: backfill N prior days
    - `--include_forms`: optional filtering by form type
    - `--limit`: truncate parsed records for testing/debug

### Unit Tests
Test coverage for this orchestrator includes:
- `test_filing_metadata_orchestrator.py`: Mocks writer + collector, checks handoff and filtering logic
- `test_run_daily_metadata_ingest.py`: Verifies CLI argument parsing, orchestrator triggering

### Best Practices
- Orchestrators should only handle flow control and logging — avoid embedding business logic.
- Validation and parsing should remain in dedicated modules.
- Future enhancements may include:
    - Batch-level run IDs
    - Failure recovery hooks
    - Dependency injection for testability

### Related Pipelines
- Pipeline 2: Filing Documents Metadata (based on accession numbers from metadata)
- Pipeline 3: SGML File Download & Disk Write

See `/docs/pipeline_overview.md` (if added) for a multi-pipeline view.
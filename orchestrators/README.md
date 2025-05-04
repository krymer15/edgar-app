# Orchestrators

This module coordinates the high-level flow of filing ingestion.

## Key Classes

### `BatchSgmlIngestionOrchestrator`
- Entry point for batch SGML ingestion via `crawler.idx`.
- Supports:
  - Single-day (`run(date_str)`)
  - Multi-day backfill (`run_backfill(start_date, end_date)`)

### `SgmlDocOrchestrator`
- Handles the ingestion of a **single filing**:
  - Downloads `.txt` SGML
  - Extracts exhibits + primary doc
  - Returns structured `ParsedResultModel` dictionary

### `BaseOrchestrator`
- Shared parent with standardized logging and config support.

## Notes
- All orchestrators use normalized accession numbers (`accession_number` only).
- `run_id` is passed per batch for logging consistency.

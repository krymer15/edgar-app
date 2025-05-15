# SEC Form Type Filtering

This document describes how to use the form type filtering functionality in the Safe Harbor EDGAR AI Platform.

## CLI Usage

All pipeline scripts now support the `--include_forms` flag which allows you to specify which form types to include during ingestion. This filtering is applied as early as possible in the collection process to minimize unnecessary processing.

### Examples

#### Pipeline 1: Metadata Ingestion

```bash
# Ingest only 10-K and 8-K filings for a specific date
python scripts/crawler_idx/run_daily_metadata_ingest.py --date 2025-05-12 --include_forms 10-K 8-K

# Ingest only S-1 filings for the last 5 days
python scripts/crawler_idx/run_daily_metadata_ingest.py --backfill 5 --include_forms S-1
```

#### Pipeline 2: Documents Ingestion

```bash
# Ingest only 10-K and 8-K filing documents for a specific date
python scripts/crawler_idx/run_daily_documents_ingest.py --date 2025-05-12 --include_forms 10-K 8-K

# Limit to 10 records for testing
python scripts/crawler_idx/run_daily_documents_ingest.py --date 2025-05-12 --include_forms 10-K --limit 10
```

#### Pipeline 3: SGML Disk Ingestion

```bash
# Download only 10-K and 8-K SGML files for a specific date
python scripts/crawler_idx/run_sgml_disk_ingest.py --date 2025-05-12 --include_forms 10-K 8-K
```

#### Full Pipeline

```bash
# Run the full daily ingestion pipeline for only 10-K and 8-K filings
python scripts/crawler_idx/run_daily_pipeline_ingest.py --date 2025-05-12 --include_forms 10-K 8-K

# Run the full pipeline with form filtering and a record limit
python scripts/crawler_idx/run_daily_pipeline_ingest.py --date 2025-05-12 --include_forms 10-K 8-K --limit 50
```

## Behavior

- If `--include_forms` is provided, it will override the default form types from the config.
- If `--include_forms` is not provided, the pipeline falls back to the default forms defined in `app_config.yaml`.
- Form filtering is applied at the collector level to minimize unnecessary processing.
- When used with the full pipeline, form filtering is applied across all three stages.

## Configuration

The default form types are defined in the `app_config.yaml` file:

```yaml
crawler_idx:
  include_forms_default: [
    "8-K", "10-K", "10-Q", "S-1", "3", "4", "5", "13D", "13G", "20-F", "6-K", "13F-HR", "424B1", "S-4", "DEF 14A", "SC TO-I",
    "424B3", "424B4", "424B5", 
    ]
```

## Implementation Details

- Form filtering is implemented at the collector level using SQLAlchemy filters.
- The `include_forms` parameter is passed down from CLI to orchestrator to collector.
- Log messages show which form types are being filtered.

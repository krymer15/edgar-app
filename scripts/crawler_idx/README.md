# Crawler IDX Scripts

This directory contains CLI scripts that drive the three core pipelines for SEC EDGAR data ingestion. These scripts serve as entry points for either running the full pipeline or individual components.

## Quick Reference

| Script | Description | Pipeline |
|--------|-------------|----------|
| `run_daily_pipeline_ingest.py` | Meta-script that orchestrates all three pipelines | 1 + 2 + 3 |
| `run_daily_metadata_ingest.py` | Ingests filing metadata from crawler.idx | Pipeline 1 |
| `run_daily_documents_ingest.py` | Indexes SGML document blocks and writes to database | Pipeline 2 |
| `run_sgml_disk_ingest.py` | Downloads and stores raw SGML files to disk | Pipeline 3 |

## Full Pipeline

### run_daily_pipeline_ingest.py

This script is the primary entry point for the entire ingestion pipeline. It drives the `DailyIngestionPipeline` meta-orchestrator, which coordinates all three pipelines and handles form-specific processing.

#### Features

- Job tracking with unique job IDs for resuming interrupted runs
- Record-level status tracking to support retry of failed records
- Support for specific accession numbers or date-based ingestion
- Form type filtering for selective processing
- Configurable caching behavior

#### Usage Examples

```bash
# Basic daily ingestion for a specific date
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12

# Limit the number of records processed
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --limit 50

# Filter by form types
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --include-forms 8-K 10-Q

# Resume a job using its ID
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --job-id 1234abcd-5678-efgh-9012-ijklmnop3456

# Retry only failed records from a job
python -m scripts.crawler_idx.run_daily_pipeline_ingest --retry-failed --job-id 1234abcd-5678-efgh-9012-ijklmnop3456

# Process specific accession numbers
python -m scripts.crawler_idx.run_daily_pipeline_ingest --accessions 0001234567-25-000001 0001234567-25-000002

# Disable caching
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --no-cache
```

## Individual Pipeline Scripts

### run_daily_metadata_ingest.py (Pipeline 1)

This script runs only Pipeline 1, which downloads the SEC's `crawler.idx` file for a specified date, parses it into structured metadata records, and writes them to the `filing_metadata` table.

#### Features

- Backfill mode for processing multiple past dates
- Form type filtering
- Record limiting for testing

#### Usage Examples

```bash
# Process a single date
python -m scripts.crawler_idx.run_daily_metadata_ingest --date 2025-05-12

# Backfill for the last 7 days
python -m scripts.crawler_idx.run_daily_metadata_ingest --backfill 7

# Limit records and filter by form type
python -m scripts.crawler_idx.run_daily_metadata_ingest --date 2025-05-12 --limit 100 --include_forms 8-K 10-K
```

### run_daily_documents_ingest.py (Pipeline 2)

This script runs only Pipeline 2, which uses the metadata from Pipeline 1 to download SGML files, extract document blocks, and write document metadata to the `filing_documents` table.

#### Features

- Document-level metadata extraction
- SGML parsing with `SgmlDocumentIndexer`
- Database-based coordination with Pipeline 1

#### Usage Examples

```bash
# Process documents for a specific date
python -m scripts.crawler_idx.run_daily_documents_ingest --date 2025-05-12

# Limit records
python -m scripts.crawler_idx.run_daily_documents_ingest --date 2025-05-12 --limit 50

# Filter by form types
python -m scripts.crawler_idx.run_daily_documents_ingest --date 2025-05-12 --include_forms 8-K 10-Q
```

### run_sgml_disk_ingest.py (Pipeline 3)

This script runs only Pipeline 3, which downloads raw SGML files from the SEC and stores them to disk in an organized directory structure.

#### Features

- Writes SGML files to a structured file path
- Supports form type filtering
- Explicit disk caching enabled

#### Usage Examples

```bash
# Download SGML files for a specific date
python -m scripts.crawler_idx.run_sgml_disk_ingest --date 2025-05-12

# Filter by form types
python -m scripts.crawler_idx.run_sgml_disk_ingest --date 2025-05-12 --include_forms 8-K 10-Q
```

## Integration Points

These scripts integrate with other components:

1. **Database**: All scripts write to or read from the PostgreSQL database
2. **File System**: Pipeline 3 writes SGML files to the filesystem
3. **Form Processing**: The full pipeline script triggers form-specific processing (e.g., Form 4)
4. **Logging**: All scripts use the `report_logger` for consistent logging

## Best Practices

- **Use the Full Pipeline**: In most cases, use `run_daily_pipeline_ingest.py` for complete processing
- **Backfill with Metadata**: For historical data, use `run_daily_metadata_ingest.py` with the `--backfill` option
- **Form Filtering**: Always consider using form filtering to reduce processing time
- **Job IDs**: For long-running jobs, note the job ID for potential retry
- **Validate Dates**: SEC filings typically occur on business days; scripts will validate this
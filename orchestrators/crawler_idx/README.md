# Crawler IDX Orchestrators

This directory contains orchestrators that manage data flows based on the SEC's daily index feed (`crawler.idx`). These orchestrators are responsible for coordinating collectors, writers, and optional filters for the three core pipelines in the EDGAR data processing system.

## Meta-Orchestrator: DailyIngestionPipeline

The `DailyIngestionPipeline` is the central control point that coordinates the three main pipelines. It serves as a meta-orchestrator that:

1. Initializes and configures all three pipeline orchestrators with shared resources
2. Sequences the execution of pipelines to ensure proper data flow
3. Provides comprehensive error handling and record-level status tracking
4. Supports form-specific processing for specialized filing types (e.g., Form 4)

### Key Features

- **Shared Resources**: Uses a single SgmlDownloader instance across all pipelines to optimize memory usage and caching
- **Job Tracking**: Uses the `job_tracker` module to create and track processing jobs with unique IDs
- **Record-Level Status**: Tracks processing status on a per-accession basis to support retry of failed records
- **Transaction Management**: Maintains clean database transaction boundaries for each record
- **Schema Validation**: Validates database schema before running form-specific processing

### Usage Example

```python
from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionPipeline

# Initialize the pipeline
pipeline = DailyIngestionPipeline(use_cache=True)

# Run for a specific date with default form types
pipeline.run(target_date="2025-05-12")

# Run with filtering and limits
pipeline.run(
    target_date="2025-05-12", 
    limit=10,
    include_forms=["8-K", "10-Q"]
)

# Run for specific accession numbers
pipeline.run(process_only=["0001234567-25-000001", "0001234567-25-000002"])

# Retry failed records from an existing job
pipeline.run(
    target_date="2025-05-12",
    retry_failed=True,
    job_id="1234abcd-5678-efgh-9012-ijklmnop3456"
)
```

## Pipeline 1: FilingMetadataOrchestrator

The `FilingMetadataOrchestrator` manages Pipeline 1, which is responsible for:

- Downloading the SEC's `crawler.idx` file for a specified date
- Parsing it into `FilingMetadata` records
- Filtering records by form type (based on configuration)
- Writing the metadata to the `filing_metadata` table in Postgres

### Components

- **Collector**: `FilingMetadataCollector` - Downloads and parses the index file
- **Writer**: `FilingMetadataWriter` - Handles database upserts for metadata records

### Flow Diagram

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

### Usage Example

```python
from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator

orchestrator = FilingMetadataOrchestrator()
orchestrator.run(
    date_str="2025-05-12",
    limit=10,  # Optional - limit records (useful for testing)
    include_forms=["8-K", "10-Q"]  # Optional - filter by form type
)
```

## Pipeline 2: FilingDocumentsOrchestrator

The `FilingDocumentsOrchestrator` manages Pipeline 2, which is responsible for:

- Collecting document information from SGML files using accession numbers from Pipeline 1
- Indexing all document blocks within each SGML filing
- Extracting metadata for HTML, TXT, XML, and other document types
- Writing document metadata to the `filing_documents` table in Postgres

### Components

- **Collector**: `FilingDocumentsCollector` - Downloads SGML and extracts document records
- **Writer**: `FilingDocumentsWriter` - Handles database writes for document records
- **Downloader**: `SgmlDownloader` - Shared instance for SGML file downloading

### Flow Diagram

```text
┌────────────────────────────────┐
│  FilingDocumentsOrchestrator   │
└────────────┬───────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│ FilingDocumentsCollector                        │
│                                                 │
│ ┌─────────────────┐      ┌──────────────────┐   │
│ │ SgmlDownloader  │─────▶│ SgmlIndexerFactory│   │
│ └─────────────────┘      └────────┬─────────┘   │
│                                    │            │
│                                    ▼            │
│                          ┌─────────────────┐    │
│                          │Document extraction│   │
│                          └─────────────────┘    │
└──────────────────────────┬─────────────────────┘
                           │
             ┌─────────────▼────────────────┐
             │ FilingDocumentsWriter        │
             │ (DB transaction per batch)   │
             └──────────────────────────────┘
```

### Usage Example

```python
from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from downloaders.sgml_downloader import SgmlDownloader

# Create with a new downloader
orchestrator = FilingDocumentsOrchestrator(use_cache=True)

# Or with a shared downloader
downloader = SgmlDownloader(user_agent="Example/1.0")
orchestrator = FilingDocumentsOrchestrator(
    use_cache=True,
    write_cache=True,
    downloader=downloader
)

# Run for a specific date
orchestrator.run(target_date="2025-05-12")

# Run for specific accession numbers
orchestrator.run(accession_filters=["0001234567-25-000001"])
```

## Pipeline 3: SgmlDiskOrchestrator

The `SgmlDiskOrchestrator` manages Pipeline 3, which is responsible for:

- Downloading raw SGML files from SEC using accession numbers
- Writing SGML content to disk in an organized directory structure
- Tracking files that have been downloaded for future reference
- Supporting the disk-based cache for other components

### Components

- **Collector**: `SgmlDiskCollector` - Handles download and filesystem operations
- **Downloader**: `SgmlDownloader` - Shared instance for SGML file downloading

### Flow Diagram

```text
┌────────────────────────────────┐
│     SgmlDiskOrchestrator       │
└────────────┬───────────────────┘
             │
┌────────────▼────────────────────────────┐
│ SgmlDiskCollector                       │
│                                         │
│ ┌─────────────────┐    ┌─────────────┐  │
│ │ SgmlDownloader  │───▶│ Path Manager │  │
│ └─────────────────┘    └──────┬──────┘  │
│                               │         │
│                         ┌─────▼──────┐  │
│                         │ Filesystem │  │
│                         └────────────┘  │
└─────────────────────────────────────────┘
```

### Usage Example

```python
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator
from downloaders.sgml_downloader import SgmlDownloader

# Create with a shared downloader
downloader = SgmlDownloader(user_agent="Example/1.0")
orchestrator = SgmlDiskOrchestrator(
    use_cache=True,
    write_cache=True,
    downloader=downloader
)

# Run for a specific date
written_files = orchestrator.run(target_date="2025-05-12")

# Run for specific accession numbers
written_files = orchestrator.run(accession_filters=["0001234567-25-000001"])
```

## CLI Integration

Each orchestrator has a dedicated CLI script for standalone operation:

- **Pipeline 1**: `scripts/crawler_idx/run_daily_metadata_ingest.py`
- **Pipeline 2**: `scripts/crawler_idx/run_daily_documents_ingest.py`
- **Pipeline 3**: `scripts/crawler_idx/run_sgml_disk_ingest.py`
- **All Pipelines**: `scripts/crawler_idx/run_daily_pipeline_ingest.py`

### CLI Arguments

Each script supports a consistent set of arguments:

- `--date YYYY-MM-DD` - Target date for processing
- `--include-forms FORM1 FORM2...` - Filter by form types
- `--accessions ACC1 ACC2...` - Process specific accession numbers

The `--limit` parameter has a standardized behavior across orchestrators:

- In `run_daily_pipeline_ingest.py` - Limits both metadata collection and the number of accession numbers processed
- In `run_daily_metadata_ingest.py` - Limits the number of filing records to collect
- **Important**: When specific accessions are provided via `--accessions`, the limit is ignored
- This ensures all documents within a selected filing are processed completely
- The limit is applied as early as possible in the process for better performance

For the meta-orchestrator (`run_daily_pipeline_ingest.py`), additional arguments include:

- `--job-id UUID` - Track or resume a specific job
- `--retry-failed` - Retry only failed records from a job
- `--no-cache` - Disable SGML cache usage

## Unit Tests

Test coverage for these orchestrators includes:

- `tests/crawler_idx/test_filing_metadata_orchestrator.py`
- `tests/crawler_idx/test_filing_documents_orchestrator.py`
- `tests/crawler_idx/test_daily_ingestion_pipeline.py`
- `tests/crawler_idx/test_run_daily_pipeline_ingest.py`

## Best Practices

- **Orchestrators should only handle flow control** - Business logic belongs in collectors, parsers, and writers
- **Share resources** - Use dependency injection to share downloaders and other costly resources
- **Respect the pipeline hierarchy** - Pipeline 1 → Pipeline 2 → Pipeline 3 is the logical flow
- **Use record-level error handling** - Don't let one failure stop the entire batch
- **Track everything** - Use logging and status updates to maintain visibility
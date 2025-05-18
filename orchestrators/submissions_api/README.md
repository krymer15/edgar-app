# Submissions API Orchestrators

This directory contains orchestrators for the SEC's Company Submissions API. While this pipeline is still active, it represents an older approach that will be updated in the future.

## SubmissionsIngestionOrchestrator

The `SubmissionsIngestionOrchestrator` manages the collection and processing of company filing data directly from the SEC's Submissions API, rather than from the daily index files.

### Key Features

- **CIK-Based Collection**: Retrieves filings for a specific company by CIK
- **Form Type Filtering**: Supports filtering by form types (e.g., 8-K, 10-K)
- **HTML Document Download**: Downloads the primary HTML document for each filing
- **Simple Error Handling**: Basic try/except pattern for processing each filing

### Architecture

The orchestrator follows a simple linear flow:
1. Collect filing metadata via the Submissions API
2. For each filing, download the HTML content
3. Write the content to the filesystem using path conventions

### Code Example

```python
# Basic usage pattern
orchestrator = SubmissionsIngestionOrchestrator(
    collector=submissions_collector,
    downloader=sec_downloader,
    writer=file_writer
)

# Process filings for a specific company
orchestrator.orchestrate(
    cik="0001234567",  # Company CIK
    limit=5  # Only process most recent 5 filings
)
```

### Integration Points

This orchestrator works with:
- `scripts/submissions_api/ingest_submissions.py` - Database ingestion script
- Models: `CompaniesMetadata` and `SubmissionsMetadata`

## Future Development

This pipeline is slated for updates that will:
- Align with the architecture patterns used in the crawler_idx pipelines
- Improve error handling and logging
- Add more robust transaction management
- Enhance integration with the rest of the EDGAR processing system
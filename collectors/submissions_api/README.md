# Submissions API Collectors

This directory contains collector components for working with the SEC's Company Submissions API. While this pipeline is still active, it represents an older approach that will be updated in the future.

## SubmissionsCollector

The `SubmissionsCollector` retrieves filing metadata for a specific company directly from the SEC's Submissions API.

```python
from collectors.submissions_api.submissions_collector import SubmissionsCollector

collector = SubmissionsCollector(user_agent="Example/1.0")

# Retrieve all filings for a company
filings = collector.collect(cik="0001234567")

# Retrieve only specific form types
filings = collector.collect(
    cik="0001234567", 
    forms_filter=["8-K", "10-K"]
)
```

### Key Features

- Retrieves filing metadata directly from the SEC's Submissions API
- Accesses company-specific data using CIK numbers
- Supports filtering by form type
- Provides URLs for accessing primary documents
- Returns data in a dictionary format ready for database insertion

### Implementation Details

- Uses `SECDownloader` to retrieve JSON data from the SEC API
- Normalizes CIK numbers to the 10-digit format required by the SEC
- Extracts key filing metadata including:
  - Accession numbers
  - Form types
  - Filing dates
  - Primary document information
  - XBRL flags
  - Item codes (for 8-K filings)
- Constructs download URLs for primary documents

### Usage in the Pipeline

The `SubmissionsCollector` is primarily used by the `SubmissionsIngestionOrchestrator` to:

1. Retrieve filing metadata for specified companies by CIK
2. Filter for filings of interest (by form type)
3. Provide document URLs for downstream components to download content

## Integration with Other Components

- **Orchestration**: Used by `orchestrators/submissions_api/submissions_ingestion_orchestrator.py`
- **Database Integration**: Collected data is written to `companies_metadata` and `submissions_metadata` tables
- **URL Generation**: Relies on `utils/url_builder.py` for consistent URL formatting

## Limitations

- Only accesses the most recent filings (limited by the SEC API's "recent" data)
- Requires knowing a company's CIK number in advance
- Does not directly download filing content (handled by downstream components)

## Future Development

This collector is planned for updates that will:
- Better integrate with the collector pattern used in the crawler_idx pipelines
- Support more robust error handling and retries
- Add pagination support for retrieving larger filing sets
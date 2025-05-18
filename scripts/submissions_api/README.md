# Submissions API Scripts

This directory contains scripts for working with the SEC's Company Submissions API, which provides direct access to company filing data. While this pipeline is still active, it represents an older approach that will be updated in the future.

## Available Scripts

### ingest_submissions.py

This script ingests company submissions data from JSON files into the database. It's designed for processing JSON files that have been downloaded from the SEC's Submissions API.

#### Features

- Parses JSON data containing company and filing information
- Writes to two database tables:
  - `companies_metadata`: Company information (CIK, name, address, etc.)
  - `submissions_metadata`: Filing metadata (accession number, form type, dates, etc.)
- Handles different date formats in the SEC API responses
- Supports batch processing of multiple JSON files

#### Usage

```bash
# Process all JSON files in the data/raw/submissions/ directory
python -m scripts.submissions_api.ingest_submissions
```

#### Expected Input Format

The script expects JSON files in the format provided by the SEC's Submissions API, similar to:

```json
{
  "cik": "0001234567",
  "name": "EXAMPLE COMPANY INC",
  "sic": "7370",
  "sicDescription": "Software Services",
  "entityType": "Corporation",
  "tickers": ["EXMPL"],
  "exchanges": ["NASDAQ"],
  "filings": {
    "recent": {
      "accessionNumber": ["0001234567-23-000123", "0001234567-23-000124"],
      "filingDate": ["2023-03-15", "2023-02-28"],
      "form": ["10-K", "8-K"],
      "primaryDocument": ["Form10K.htm", "Form8K.htm"],
      "items": ["","Item 2.02"]
    }
  }
}
```

#### Database Schema

The script populates the following tables:

1. **companies_metadata**:
   - Primary key: `cik`
   - Contains company information including name, tickers, entity type, SIC code, etc.

2. **submissions_metadata**:
   - Primary key: `accession_number`
   - Foreign key: `cik` references `companies_metadata(cik)`
   - Contains filing metadata including form type, filing date, report date, etc.

## Integration with Orchestrators

This script works in conjunction with the `SubmissionsIngestionOrchestrator` from the `orchestrators/submissions_api` directory. The typical workflow is:

1. Use the orchestrator to download company submissions JSON data
2. Store the JSON files in `data/raw/submissions/`
3. Run this script to parse and ingest the data into the database

## Future Development

This pipeline is planned for updates that will:

- Integrate more closely with the crawler_idx pipeline architecture
- Add more robust error handling and logging
- Enhance the data model to support more detailed analysis
- Provide better filtering and processing options

## Related Components

- `orchestrators/submissions_api/submissions_ingestion_orchestrator.py` - Orchestrator for this pipeline
- `collectors/submissions_api/submissions_collector.py` - Collector for SEC Submissions API data
- `models/submissions.py` and `models/companies.py` - Database models used by this script
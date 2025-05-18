# CLI Scripts

This directory contains scripts that serve as entry points for running various EDGAR data processing pipelines. These scripts are designed to be invoked directly from the command line, used in scheduled tasks, or called by meta-orchestrators.

## Directory Structure

```
scripts/
│
├── crawler_idx/                # Daily index processing scripts
│   ├── run_daily_pipeline_ingest.py     # Meta-script for all pipelines
│   ├── run_daily_metadata_ingest.py     # Pipeline 1 (metadata)
│   ├── run_daily_documents_ingest.py    # Pipeline 2 (documents)
│   └── run_sgml_disk_ingest.py          # Pipeline 3 (SGML download)
│
├── forms/                      # Form-specific processing scripts
│   └── run_form4_ingest.py             # Form 4 specialized processing
│
├── submissions_api/            # SEC Submissions API scripts
│   └── ingest_submissions.py           # Process company submissions data
│
├── tools/                      # Utility and debug scripts
│   ├── debug_form_filtering.py         # Test form type filtering
│   ├── debug_form_validation.py        # Debug form type validation
│   └── test_form_validation.py         # Test form validation logic
│
└── devtools/                   # Development tools
    ├── cleanup_test_data.py            # Clean test data
    ├── clear_test_records.py           # Clear test records from DB
    ├── process_company_filings.py      # Process filings for a company
    └── test_postgres_connection.py     # Test database connection
```

## Core Pipelines (crawler_idx)

These scripts process data from the SEC's daily index feed (`crawler.idx`).

### run_daily_pipeline_ingest.py

Runs all three ingestion pipelines (metadata → documents → SGML download) with intelligent coordination.

```bash
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --limit 100
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --include-forms 10-K 8-K
python -m scripts.crawler_idx.run_daily_pipeline_ingest --retry-failed --job-id <uuid>
```

**Args:**
- `--date`: Target SEC filing date (YYYY-MM-DD)
- `--limit`: Max filings to process
- `--include-forms`: Form types to include (e.g., 10-K 8-K)
- `--job-id`: Job ID for continuing an existing job
- `--retry-failed`: Retry failed records (requires --job-id)
- `--accessions`: Process specific accession numbers
- `--no-cache`: Disable SGML cache usage

### run_daily_metadata_ingest.py (Pipeline 1)

Collects and writes filing metadata for a target date or backfill range.

```bash
python -m scripts.crawler_idx.run_daily_metadata_ingest --date 2025-05-12
python -m scripts.crawler_idx.run_daily_metadata_ingest --backfill 3
```

**Args:**
- `--date`: Single target date (YYYY-MM-DD)
- `--backfill`: Backfill N previous valid filing days
- `--limit`: Max filings per day
- `--include_forms`: Form types to include (e.g., --include_forms 10-K 8-K)

### run_daily_documents_ingest.py (Pipeline 2)

Indexes all SGML filings into structured document records.

```bash
python -m scripts.crawler_idx.run_daily_documents_ingest --date 2025-05-12 --limit 100
```

**Args:**
- `--date` (required): Target date
- `--limit`: Max filings to process
- `--include_forms`: Form types to include

### run_sgml_disk_ingest.py (Pipeline 3)

Writes raw .txt SGML submissions to disk (e.g., for archiving or debugging).

```bash
python -m scripts.crawler_idx.run_sgml_disk_ingest --date 2025-05-12
```

**Args:**
- `--date` (required): Target date
- `--include_forms`: Form types to include

## Form-Specific Scripts (forms)

These scripts provide specialized processing for specific SEC form types.

### run_form4_ingest.py

Processes Form 4 filings (Statement of Changes in Beneficial Ownership).

```bash
python -m scripts.forms.run_form4_ingest --date 2025-05-12
python -m scripts.forms.run_form4_ingest --accessions 0001234567-25-000123
```

**Args:**
- `--date`: Target date (YYYY-MM-DD)
- `--accessions`: Specific accession numbers to process
- `--limit`: Limit number of records processed
- `--reprocess`: Reprocess records even if already processed
- `--write-xml`: Write raw XML content to disk
- `--cache`: Use file cache (default is False for pipelines)

## Submissions API Scripts (submissions_api)

These scripts work with the SEC's Company Submissions API.

### ingest_submissions.py

Processes company submissions data from JSON files into the database.

```bash
python -m scripts.submissions_api.ingest_submissions
```

This script processes all JSON files in the `data/raw/submissions/` directory, extracting company metadata and filing information into the database tables.

## Filtering by Form Type

Most scripts support form type filtering via the `--include_forms` parameter:

```bash
python -m scripts.crawler_idx.run_daily_metadata_ingest --date 2025-05-10 --include_forms 10-K 8-K S-1
```

If not provided, it defaults to the form types defined under `crawler_idx.include_forms_default` in `app_config.yaml`.

Form type validation is handled by the `FormTypeValidator` class, which supports various form type formats and normalizations.

## Common Features

All scripts support:
- Config-based logging via `utils/report_logger.py`
- Clean exit codes and stdout/stderr integration for use in Airflow or cron
- Form type validation and normalization
- Consistent parameter naming across scripts

### Script Header

All scripts in this directory follow this standard pattern to ensure the project root is properly added to the Python path:

```python
# scripts/your_module/your_script.py

import argparse
import sys, os

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

# Now you can import project modules
from utils.report_logger import log_info
```

This pattern is used instead of direct imports to maintain compatibility across different execution environments.

## Usage in Production

When running these scripts in production:

1. **Daily Ingestion**: Use `run_daily_pipeline_ingest.py` for complete processing
2. **Selective Processing**: Use pipeline-specific scripts when you only need part of the process
3. **Specialized Forms**: Use form-specific scripts for optimized processing
4. **Backfilling**: Use `run_daily_metadata_ingest.py --backfill N` for historical data
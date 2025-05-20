# Utilities

This directory contains utility modules that provide shared functionality across the EDGAR data processing system. These utilities support path management, configuration, logging, validation, and other cross-cutting concerns.

## Core Utilities

### Path Management

#### path_manager.py

Manages file path generation for raw and processed files, ensuring consistent directory structures. All paths are relative to the symlinked `data/` directory.

```python
from utils.path_manager import build_raw_filepath

# Generate a path for storing a raw file
filepath = build_raw_filepath(
    year="2025",
    cik="0001234567",
    form_type="10-K",
    accession_or_subtype="000123456725000123",
    filename="filing.html"
)
# Result: data/raw/2025/0001234567/10-K/000123456725000123/filing.html
```

#### build_raw_filepath_by_type

Creates type-specific file paths for different data types:

```python
from utils.path_manager import build_raw_filepath_by_type

# Generate a path for an SGML file
sgml_path = build_raw_filepath_by_type(
    file_type="sgml",
    year="2025",
    cik="0001234567",
    form_type="10-K",
    accession_or_subtype="000123456725000123",
    filename="submission.txt"
)
# Result: data/raw/sgml/0001234567/2025/10-K/000123456725000123/submission.txt
```

> **Note:** The actual target directory for `data/` is typically a symlink pointing to external storage. This keeps large files out of the Git repository. The paths shown in examples are relative to wherever the symlinked `data/` directory actually points. See the main README.md for details on symlink setup.

### Logging

#### report_logger.py

Provides structured logging functions for consistent log output across the application.

```python
from utils.report_logger import log_info, log_warn, log_error

# Log at different levels
log_info("Processing started")
log_warn("Missing field: description")
log_error("Failed to download filing")

# Append structured data to CSV reports
from utils.report_logger import append_ingestion_report
append_ingestion_report({
    "record_type": "parsed",
    "accession_number": "0001234567-25-000123",
    "cik": "0001234567",
    "form_type": "10-K",
    "filing_date": "2025-04-01"
})
```

### Configuration

#### get_project_root.py

Utility to determine the project root directory regardless of where the script is run from.

```python
from utils.get_project_root import get_project_root

# Get the project root path
root_path = get_project_root()
```

This utility is used by critical components like `report_logger.py` and `config_loader.py` to ensure consistent path resolution. Many test and script files also use a similar pattern directly with `sys.path.insert` (see "Universal Script Header" below).

### Process Management

#### job_tracker.py

Tracks long-running jobs and their progress across multiple batches.

```python
from utils.job_tracker import create_job, get_job_progress, update_record_status

# Create a job
job_id = create_job("2025-05-12", "Daily ingestion for May 12")

# Update status of a record
update_record_status("0001234567-25-000123", "completed")

# Get job progress
progress = get_job_progress(job_id)
print(f"Job is {progress['progress_pct']}% complete")
```

## SEC-Specific Utilities

### Form Validation

#### form_type_validator.py

Validates and normalizes SEC form types using rules from configuration.

```python
from utils.form_type_validator import FormTypeValidator

# Validate a list of form types
form_types = ["10-K", "10k", "S-1/A"]
validated = FormTypeValidator.get_validated_form_types(form_types)

# Check if a form type is valid
is_valid = FormTypeValidator.is_valid_form_type("8-K")
```

### URL Construction

#### url_builder.py

Builds SEC EDGAR URLs for different data sources. 

**Important Note on CIK Selection (Bug 8 Fix):**
The SEC EDGAR system creates multiple URL paths for the same filing, one for each involved entity. For example, a Form 4 filing can be accessed through the issuer's CIK path or any of the reporting owners' CIK paths. Despite these multiple URL paths, there's only one actual filing identified by a unique accession number.

**Standardization Guidelines:**
- For Form 4 filings: Always use the issuer CIK for URL construction
  - Form4Orchestrator extracts this directly from the XML content
  - Form4SgmlIndexer provides the issuer CIK in its index_documents return value
  - This ensures consistent URL construction regardless of which CIK was initially used
- For most other filings: Use the primary filer's CIK (usually the company filing the form)

```python
from utils.url_builder import construct_sgml_txt_url, construct_submission_json_url

# Get URL for SGML submission file (with issuer CIK for Form 4s)
sgml_url = construct_sgml_txt_url("0001234567", "000123456725000123")

# Get URL for company submissions JSON
submissions_url = construct_submission_json_url("0001234567")
```

**URL Functions:**
- `construct_primary_document_url`: For accessing specific documents within a filing
- `construct_submission_json_url`: For accessing a company's submissions metadata
- `construct_filing_index_url`: For accessing a filing's index page
- `construct_sgml_txt_url`: For accessing the raw SGML text of a filing

### SEC Calendar

#### filing_calendar.py

Handles SEC filing calendar logic, including holidays and valid filing days.

```python
from utils.filing_calendar import is_valid_filing_day
from datetime import date

# Check if a date is a valid SEC filing day
is_valid = is_valid_filing_day(date(2025, 5, 12))
```

### Ticker-CIK Mapping

#### ticker_cik_mapper.py

Maps stock ticker symbols to SEC Central Index Keys (CIKs).

```python
from utils.ticker_cik_mapper import TickerCIKMapper

# Initialize the mapper
mapper = TickerCIKMapper()

# Get CIK for a ticker
cik = mapper.get_cik("AAPL")
```

## Data Handling Utilities

### Accession Number Formatting

#### accession_formatter.py

Consistently formats accession numbers for different contexts (database, URLs, filenames).

```python
from utils.accession_formatter import format_for_db, format_for_url, format_for_filename

# Format for database storage (with dashes)
db_format = format_for_db("000123456725000123")  # 0001234567-25-000123

# Format for SEC URLs (no dashes)
url_format = format_for_url("0001234567-25-000123")  # 000123456725000123

# Format for filenames (no dashes)
filename_format = format_for_filename("0001234567-25-000123")  # 000123456725000123
```

### SGML Utilities

#### sgml_utils.py

Utilities for working with SGML files, including downloading and extracting metadata.

```python
from utils.sgml_utils import download_sgml_for_accession, extract_issuer_cik_from_sgml

# Download SGML content
sgml_content = download_sgml_for_accession(
    cik="0001234567",
    accession_number="0001234567-25-000123",
    user_agent="Example-App/1.0"
)

# Extract issuer CIK from SGML content
issuer_cik = extract_issuer_cik_from_sgml(sgml_content)
```

### Cache Management

#### cache_manager.py

Manages the disk cache for downloaded SGML files.

```python
from utils.cache_manager import clear_sgml_cache

# Clear all cache files for a specific CIK
cleared_count = clear_sgml_cache(cik="0001234567")
print(f"Cleared {cleared_count} cache files")
```

## Usage Patterns

### 1. Path Generation

Used by all components that read from or write to the filesystem:
- Downloaders use these to save downloaded files
- Writers use these to determine where to write parsed results
- Collectors use these to locate cached files

### 2. Logging

Used across the system for consistent log formats and levels:
- Orchestrators log progress and errors
- Writers log successful/failed writes
- CLI scripts use these for user feedback

### 3. Form Type Validation

Used by:
- Command-line arguments in scripts
- Filtering logic in collectors and orchestrators
- Database query filters

### 4. Job Tracking

Used by:
- DailyIngestionPipeline for managing multi-record processing
- CLI scripts for tracking long-running jobs
- Status reporting in orchestrators

## Universal Script Header

Many scripts and test files in the project use this pattern (sometimes called the "Universal Script Header") to ensure proper module imports:

```python
import sys, os

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

# Now you can safely import project modules
from utils.report_logger import log_info
```

This pattern serves a similar purpose to `get_project_root.py` but is used directly in scripts and tests to ensure they can find all project modules regardless of where they're run from. It's particularly important for:

- Test files that need to access modules from different parts of the codebase
- CLI scripts that may be run directly or via Python's `-m` flag
- Development tools and utilities 

## Best Practices

1. **Prefer utility functions over reinventing logic**: Most common operations like path building, logging, and validation are already handled by utility modules.

2. **Keep utils stateless where possible**: Utilities should be predominantly stateless, accepting inputs and returning outputs without maintaining internal state.

3. **Consistent pattern usage**: When implementing similar functionality:
   - For paths: Use path_manager functions
   - For logging: Use report_logger functions
   - For accession numbers: Use accession_formatter functions
   - For project root access: Use get_project_root() in core modules or the Universal Script Header in scripts/tests

4. **Avoid circular imports**: Some utilities like report_logger use lazy loading to avoid circular import issues.
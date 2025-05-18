# Form-Specific Scripts

This directory contains CLI scripts for processing specific SEC form types. These scripts provide targeted functionality for extracting and processing data from particular form types, with each form type having unique data structures and requirements.

## Current Scripts

### run_form4_ingest.py

This script drives the `Form4Orchestrator` to process SEC Form 4 filings (Statement of Changes in Beneficial Ownership). It handles the specialized extraction of XML data from within SGML container files, parsing the XML content, and writing the data to specialized database tables.

#### Features

- Processes Form 4 filings by date or specific accession numbers
- Extracts and parses embedded XML from SGML container files
- Writes structured data to form4_filings, form4_relationships, and form4_transactions tables
- Optionally writes extracted XML to disk for inspection or backup
- Supports reprocessing of previously processed filings
- Detailed result reporting including success/failure counts

#### Usage Examples

```bash
# Process Form 4 filings for a specific date
python -m scripts.forms.run_form4_ingest --date 2025-05-12

# Process specific accession numbers (Form 4 filings)
python -m scripts.forms.run_form4_ingest --accessions 0000123456-25-000123 0000123456-25-000124

# Limit the number of records processed
python -m scripts.forms.run_form4_ingest --date 2025-05-12 --limit 10

# Reprocess already processed filings
python -m scripts.forms.run_form4_ingest --date 2025-05-12 --reprocess

# Write extracted XML content to disk
python -m scripts.forms.run_form4_ingest --date 2025-05-12 --write-xml

# Use file caching (default is off in pipeline)
python -m scripts.forms.run_form4_ingest --date 2025-05-12 --cache
```

#### Integration with Main Pipeline

While this script can be run independently, the Form 4 processing is also integrated into the full `DailyIngestionPipeline` when run via `scripts/crawler_idx/run_daily_pipeline_ingest.py`. The pipeline automatically detects Form 4 filings and triggers specialized processing.

#### Database Schema Requirements

For Form 4 processing to work, the following database tables must exist:
- `entities` - Stores information about issuers and reporting persons
- `form4_filings` - Contains the core filing metadata
- `form4_relationships` - Maps the relationships between reporting persons and issuers
- `form4_transactions` - Records individual stock transactions

## Adding New Form Scripts

When adding scripts for other form types, follow these guidelines:

1. **Use the Base Pattern**: Follow the pattern established by `run_form4_ingest.py`
2. **Create a Specialized Orchestrator**: Implement a form-specific orchestrator first
3. **Support Both Modes**: Allow processing by date or specific accession numbers
4. **Provide Result Reporting**: Include detailed success/failure stats
5. **Documentation**: Include usage examples and required database schema information

### Script Template

```python
#!/usr/bin/env python
# scripts/forms/run_formX_ingest.py

"""
Run Form X data processing for a specific date or accession numbers.

This script processes Form X filings by:
1. [Description of step 1]
2. [Description of step 2]
3. [Description of step 3]

Usage:
    python scripts/forms/run_formX_ingest.py --date 2025-05-12
    python scripts/forms/run_formX_ingest.py --accessions 0000123456-25-000123
"""

import argparse
from orchestrators.forms.formX_orchestrator import FormXOrchestrator
from utils.report_logger import log_info

def main():
    parser = argparse.ArgumentParser(description="Run Form X data processing")
    
    # Required mutually exclusive group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--date", type=str, help="Target date (YYYY-MM-DD)")
    input_group.add_argument("--accessions", nargs="+", help="Specific accession numbers")
    
    # Add form-specific options
    # [Additional arguments]
    
    args = parser.parse_args()
    orchestrator = FormXOrchestrator()
    
    try:
        results = orchestrator.run(
            target_date=args.date,
            accession_filters=args.accessions
        )
        
        log_info(f"Form X processing complete: {results['succeeded']} succeeded, {results['failed']} failed")
    except Exception as e:
        log_error(f"Error running Form X processor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```
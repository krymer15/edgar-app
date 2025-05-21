# Form-Specific Orchestrators

This directory contains orchestrators specialized for processing particular SEC form types. Each form orchestrator handles the unique extraction, parsing, and persistence requirements of a specific form type.

## Current Form Orchestrators

### Form4Orchestrator

The `Form4Orchestrator` is responsible for specialized processing of Form 4 filings (Statement of Changes in Beneficial Ownership). It:

1. Extracts Form 4 XML data from SGML container files
2. Parses the XML into structured entity, relationship, and transaction data, including acquisition/disposition flags
3. Writes the data to the specialized Form 4 database tables

#### Key Features

- **Integration with DailyIngestionPipeline**: Can work standalone or as part of the daily pipeline
- **Content Retrieval Strategy**: Uses a memory → disk → download hierarchy for content retrieval
- **XML Extraction**: Uses `Form4SgmlIndexer` to extract XML from SGML containers
- **Entity Relationship Modeling**: Maintains the complex relationships between issuers, reporting persons, and transactions
- **Transaction Processing**: Handles the diverse transaction types and reporting requirements
- **Acquisition/Disposition Tracking**: Captures whether securities were acquired (A) or disposed (D) in each transaction
- **CIK Standardization (Bug 8 Fix)**: Reliably extracts the issuer CIK from Form 4 XML content and uses it consistently for URL construction, file paths, and RawDocument creation. This ensures:
  - Consistent handling across the pipeline
  - All XML files are stored under the issuer CIK directory structure
  - Files are correctly organized by the company whose securities are being traded
  - The same accession number is found under a single logical path
  - SEC EDGAR's multiple URL paths (one per involved entity) are reconciled to a single canonical path

- **Pipeline Integration**: Seamlessly integrates with the DailyIngestionPipeline through:
  - Shared downloader instances for efficient resource usage
  - Compatible processing status tracking with the main pipeline
  - Common configuration patterns for consistent setup
  - Reuse of existing file caching mechanisms

#### Internal Components

- **Form4SgmlIndexer**: Specialized indexer that extracts XML content from Form 4 SGML files
- **Form4Writer**: Database writer that handles the complex entity-relationship model:
  - Creates/updates entities in the universal registry
  - Creates relationships between issuers and reporting owners
  - Writes transaction data with proper references
  - Updates filing processing status for tracking
  - Supports both initial creation and updates to existing records

#### Error Handling

The Form4Orchestrator provides robust error handling throughout the processing pipeline:

- Graceful handling of download failures with informative error messages
- Parsing error detection and reporting for both SGML and XML content
- Database error recovery with transaction management
- Comprehensive status tracking through the filing_metadata table
- Detailed error messages stored for debugging and troubleshooting
- Ability to retry failed operations with appropriate backoff

#### Database Tables

The Form 4 data model spans multiple tables:
- `entities`: Stores information about issuers and reporting persons
- `form4_filings`: Contains the core filing metadata
- `form4_relationships`: Maps the relationships between reporting persons and issuers
- `form4_transactions`: Records individual stock transactions

#### Flow Diagram

```text
┌────────────────────────────┐
│     Form4Orchestrator      │
└────────────┬───────────────┘
             │
┌────────────▼────────────────────────────────────┐
│ Content Retrieval Strategy                      │
│                                                 │
│  ┌───────────────┐   ┌────────────┐   ┌───────┐ │
│  │ Memory Cache  │──▶│ Disk Cache │──▶│ SEC   │ │
│  └───────────────┘   └────────────┘   └───────┘ │
└─────────────────────┬──────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────┐
│ Form4SgmlIndexer                               │
│                                                │
│  ┌────────────────┐    ┌────────────────────┐  │
│  │ SGML Processing│───▶│ XML Content Extract│  │
│  └────────────────┘    └──────────┬─────────┘  │
└────────────────────────────────────┬───────────┘
                                     │
┌────────────────────────────────────▼───────────┐
│ Form4Writer                                    │
│                                                │
│  ┌─────────┐   ┌────────────┐   ┌────────────┐ │
│  │ Entities│──▶│Relationships│──▶│Transactions│ │
│  └─────────┘   └────────────┘   └────────────┘ │
└────────────────────────────────────────────────┘
```

#### Usage Example

```python
from orchestrators.forms.form4_orchestrator import Form4Orchestrator
from downloaders.sgml_downloader import SgmlDownloader

# Create with a shared downloader (from DailyIngestionPipeline)
downloader = SgmlDownloader(user_agent="Example/1.0")
orchestrator = Form4Orchestrator(
    use_cache=True,
    write_cache=False,
    downloader=downloader
)

# Run for specific accession numbers
results = orchestrator.run(
    accession_filters=["0001234567-25-000001"],
    write_raw_xml=True  # Optionally write the extracted XML to disk
)

# Run for a specific date
results = orchestrator.run(
    target_date="2025-05-12",
    limit=10,  # Optional limit
    reprocess=False  # Skip already processed filings
)

# Check the results
print(f"Processed: {results['processed']}")
print(f"Succeeded: {results['succeeded']}")
print(f"Failed: {results['failed']}")
```

#### CLI Integration

The Form 4 orchestrator has a dedicated CLI script:
- `scripts/forms/run_form4_ingest.py`

This script supports the following arguments:
- `--date YYYY-MM-DD` - Target date for processing
- `--limit N` - Limit the number of records processed
- `--accessions ACC1 ACC2...` - Process specific accession numbers
- `--reprocess` - Reprocess filings even if already in the database
- `--write-xml` - Write extracted XML to disk for inspection/backup

## Adding New Form Orchestrators

When adding a new form orchestrator, follow these guidelines:

1. **Inherit from BaseOrchestrator**: All form orchestrators should extend the base class
2. **Implement Content Extraction**: Create specialized indexers for the form's container format
3. **Custom Writers**: Create form-specific writers that handle the data model
4. **DailyIngestionPipeline Integration**: Add hooks in the pipeline for specialized processing
5. **Schema Validation**: Check for required tables before attempting to process
6. **Resource Sharing**: Support shared downloaders when possible
7. **Error Handling**: Implement record-level error handling and status tracking

### Template for New Form Orchestrators

```python
from orchestrators.base_orchestrator import BaseOrchestrator
from downloaders.base_downloader import BaseDownloader
from utils.report_logger import log_info, log_error

class Form<TYPE>Orchestrator(BaseOrchestrator):
    def __init__(self, use_cache: bool = True, write_cache: bool = True, 
                 downloader: BaseDownloader = None):
        self.use_cache = use_cache
        self.write_cache = write_cache
        self.downloader = downloader or DefaultDownloader(use_cache=use_cache)
        
    def orchestrate(self, target_date: str = None, limit: int = None,
                   accession_filters: list[str] = None, reprocess: bool = False):
        # 1. Get filings to process
        # 2. Extract form-specific content
        # 3. Parse content into structured data
        # 4. Write to database
        pass
        
    def run(self, target_date: str = None, limit: int = None,
           accession_filters: list[str] = None, reprocess: bool = False):
        """Public API with additional logging"""
        log_info(f"Starting Form<TYPE> processing")
        results = self.orchestrate(target_date, limit, accession_filters, reprocess)
        log_info(f"Completed Form<TYPE> processing")
        return results
```
# Form 4 Processing Module

This module provides specialized logic for processing SEC Form 4 filings (Changes in Beneficial Ownership).

## Overview

Form 4 filings have a unique structure that involves multiple entities in different roles:
- **Issuer**: The company whose securities are being traded
- **Reporting Owners**: Insiders (executives, directors, etc.) who are trading the securities
- **Relationships**: The connections between issuers and owners (director, officer, 10% owner)
- **Transactions**: The actual securities transactions being reported

This module implements a multi-CIK relationship model to accurately represent these relationships.

## Database Schema

The Form 4 schema consists of several related tables:

1. **entities**: Universal registry for all entities (companies, people, etc.)
2. **form4_filings**: Core Form 4 filing information linked to filing_metadata
3. **form4_relationships**: Relationships between issuers and reporting owners
4. **form4_transactions**: Individual transactions reported in the filing

## Components

### Parsers/Indexers

- **Form4SgmlIndexer**: Specialized parser for Form 4 SGML files that extracts:
  - Issuer data (CIK, name)
  - Reporting owner data (CIK, name)
  - Relationship information (director, officer, etc.)
  - Transaction details
  - Period of report
  - XML content (when available)

### Writers

- **Form4Writer**: Handles the database operations for Form 4 data:
  - Creates/updates entities in the universal registry
  - Creates relationships between issuers and reporting owners
  - Writes transaction data
  - Updates filing processing status
  - Supports both initial creation and updates to existing records

### Orchestrators

- **Form4Orchestrator**: Coordinates the end-to-end Form 4 processing flow:
  - Integrates with the daily ingestion pipeline
  - Retrieves SGML content (from memory cache, disk cache, or direct download)
  - Parses SGML using Form4SgmlIndexer
  - Writes data using Form4Writer
  - Handles error cases and maintains processing status
  - Provides result tracking and reporting

### CLI Tools

- **run_form4_ingest.py**: Command-line tool for processing Form 4 filings

## Usage

### Process a Specific Form 4 Filing

```bash
python scripts/forms/run_form4_ingest.py --accession 0001234567-25-000001 --date 2025-05-15
```

### Process All Form 4 Filings for a Date

```bash
python scripts/forms/run_form4_ingest.py --date 2025-05-15 --limit 100
```

## Implementation Details

### SGML/XML Processing
The Form4SgmlIndexer handles both pure SGML format and XML format within SGML wrappers. For each filing:
1. The indexer first attempts to extract the XML content from the SGML
2. If XML is found, it's parsed using XML-specific parsers
3. If XML is not available or cannot be parsed, fallback SGML parsers are used
4. Multiple extraction strategies are employed for robustness

### Multi-CIK Relationship Model
The implementation supports:
- Multiple reporting owners in a single filing
- Proper relationship tracking between issuers and reporting owners
- Different relationship types (director, officer, 10% owner, other)
- Tracking officer titles and other relationship details

### Error Handling
The Form4Orchestrator provides robust error handling:
- Graceful handling of download failures
- Parsing error detection and reporting
- Database error recovery
- Comprehensive status tracking through the filing_metadata table
- Detailed error messages stored for debugging

### Integration with Daily Ingestion Pipeline
The Form 4 module integrates with the existing pipeline in several ways:
- Shared downloader for efficient resource usage
- Compatible processing status tracking
- Common configuration patterns
- Reusing existing file caching mechanisms

## Data Model

The Form 4 data model provides rich relationship information:

- Track insider trading patterns across multiple companies
- Identify group filings and joint reporting
- Capture detailed transaction information including footnotes
- Support various relationship types (director, officer, 10% owner)

## Testing

The module includes comprehensive unit tests:
- Tests for Form4SgmlIndexer for accurate SGML parsing
- Tests for Form4Writer to verify database operations
- Tests for Form4Orchestrator to validate the end-to-end process
- Test fixtures for repeatable testing

## Future Extensions

This module serves as a template for handling other form types with multi-entity relationships:

- Form 3 (Initial Beneficial Ownership)
- Form 5 (Annual Beneficial Ownership)
- Form 13D/G (Beneficial Ownership Reports)
- Form 13F (Institutional Investment Manager Holdings)
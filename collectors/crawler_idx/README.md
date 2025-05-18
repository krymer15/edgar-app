# Crawler IDX Collectors

This directory contains collector components designed to work with the SEC's daily index feed (`crawler.idx`). These collectors are responsible for retrieving filing metadata, document information, and SGML content from the SEC EDGAR system.

## Overview

The crawler_idx collectors coordinate with the three main pipelines of the EDGAR data processing system:

1. **Pipeline 1**: Filing Metadata Collection - `FilingMetadataCollector`
2. **Pipeline 2**: Filing Document Collection - `FilingDocumentsCollector`
3. **Pipeline 3**: SGML File Collection - `SgmlDiskCollector`

Each collector handles a specific part of the data ingestion process, working in sequence as part of the daily ingestion pipeline.

## FilingMetadataCollector

`FilingMetadataCollector` handles the first stage of the EDGAR data processing pipeline, retrieving and parsing the SEC's daily index file.

```python
from collectors.crawler_idx.filing_metadata_collector import FilingMetadataCollector

collector = FilingMetadataCollector(user_agent="Example/1.0")
filing_metadata = collector.collect(
    date="2025-05-12",             # Date to collect metadata for
    include_forms=["10-K", "8-K"], # Optional form type filtering
    limit=50                       # Optional limit on number of records
)
```

### Key Features

- Downloads the SEC's daily `crawler.idx` file for a specified date
- Parses it into `FilingMetadata` dataclass instances
- Supports filtering by form type to limit processing to specific forms
- Handles multi-CIK filings (such as Form 4) by identifying the issuer CIK
- Performs duplicate elimination when multiple CIKs appear for the same filing

### Implementation Details

- Uses `requests` to download the daily index file
- Leverages `CrawlerIdxParser` for parsing the index file format
- Special handling for forms with issuer/reporting owner relationships (4, 3, 5, 13D, 13G)
- May download SGML content to extract issuer CIK information for proper disambiguation

## FilingDocumentsCollector

`FilingDocumentsCollector` handles the second stage of processing, extracting document metadata from SGML filings.

```python
from collectors.crawler_idx.filing_documents_collector import FilingDocumentsCollector
from downloaders.sgml_downloader import SgmlDownloader
from models.database import get_db_session

with get_db_session() as session:
    # Optional: Share a downloader instance with other components
    downloader = SgmlDownloader(user_agent="Example/1.0")
    
    collector = FilingDocumentsCollector(
        db_session=session,
        user_agent="Example/1.0",
        downloader=downloader  # Optional shared downloader
    )
    
    # Collect documents for a specific date
    documents = collector.collect(
        target_date="2025-05-12",
        limit=10,
        include_forms=["10-K", "8-K"]
    )
    
    # Or collect documents for specific accession numbers
    documents = collector.collect(
        accession_filters=["0001234567-25-000123"]
    )
```

### Key Features

- Uses filing metadata from Pipeline 1 to locate SGML filings
- Downloads SGML content using `SgmlDownloader`
- Uses `SgmlDocumentIndexer` to extract document blocks from SGML files
- Converts parsed documents to `FilingDocumentRecord` objects for database storage
- Handles special case CIK resolution for forms with issuer/reporting relationships

### Implementation Details

- Queries the database for filing metadata
- Supports filtering by date, accession number, or form types
- Identifies the correct CIK for SGML downloading (especially important for Form 4)
- Uses a shared downloader instance when provided (for memory efficiency)
- Adapts parsed documents to the ORM model for database integration

## SgmlDiskCollector

`SgmlDiskCollector` handles the third stage of processing, downloading and storing raw SGML files to disk.

```python
from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector
from downloaders.sgml_downloader import SgmlDownloader
from models.database import get_db_session

with get_db_session() as session:
    # Optional: Share a downloader instance with other components
    downloader = SgmlDownloader(user_agent="Example/1.0")
    
    collector = SgmlDiskCollector(
        db_session=session,
        user_agent="Example/1.0",
        downloader=downloader  # Optional shared downloader
    )
    
    # Write SGML files for a specific date
    written_files = collector.collect(
        target_date="2025-05-12",
        include_forms=["10-K", "8-K"]
    )
    
    # Or write SGML files for specific accession numbers
    written_files = collector.collect(
        accession_filters=["0001234567-25-000123"]
    )
```

### Key Features

- Uses document metadata from Pipeline 2 to locate source SGML files
- Downloads SGML content if not already cached
- Writes raw SGML files to disk in a structured directory hierarchy
- Handles special case CIK resolution for forms with issuer/reporting relationships
- Integrates with the `RawFileWriter` for consistent file organization

### Implementation Details

- Queries `filing_documents` table for document records
- Uses `build_raw_filepath_by_type` for consistent file path generation
- Skips already downloaded files to prevent duplicate downloads
- Converts SGML content to `RawDocument` dataclass before writing
- Returns the list of file paths where SGML content was written

## Integration with Orchestrators

These collectors are used by the orchestrators in the `orchestrators/crawler_idx` directory:

- `FilingMetadataOrchestrator` uses `FilingMetadataCollector`
- `FilingDocumentsOrchestrator` uses `FilingDocumentsCollector`
- `SgmlDiskOrchestrator` uses `SgmlDiskCollector`
- `DailyIngestionPipeline` coordinates all three pipelines

## Error Handling

All collectors implement robust error handling:

- Errors during download are logged but don't necessarily stop the entire process
- Collectors return successfully processed records even when some fail
- Specialized error handling for form types that require special CIK resolution

## Performance Considerations

- Collectors support incremental processing through accession filtering
- Shared downloader instances reduce memory usage
- Caching options help optimize repeat access to the same resources
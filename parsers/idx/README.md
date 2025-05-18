# IDX Indexer Module

This module contains the logic for indexing `crawler.idx` files published daily by the SEC. It is a core component of **Pipeline 1: Filing Metadata Ingestion**.

## Indexer Role

The `CrawlerIdxParser` class acts as an **indexer** rather than a full parser. In the codebase's terminology:

- **Indexers**: Extract document blocks, metadata, and pointers from container files
- **Parsers**: Process specific document types and extract structured data

The IDX indexer extracts filing metadata pointers from daily index files but does not process the actual filing content.

## Purpose

The `crawler.idx` file is a flat text index of all EDGAR filings submitted on a given day. It contains:
- Company Name
- Form Type
- CIK
- Filing Date
- Filing URL

`CrawlerIdxParser` transforms these flat text records into structured dataclass instances (`FilingMetadata`) used downstream for ingestion.

## Class: `CrawlerIdxParser`

### Role
- **Classification**: ✅ Indexer (not parser)
- **Input**: `List[str]` (raw lines from `crawler.idx`)
- **Output**: `List[FilingMetadata]` dataclass instances

### Responsibilities
- Locates the header break line in `.idx` (e.g. "-----")
- Extracts each filing's core fields
- Parses the date format (YYYYMMDD)
- Extracts accession number from the URL
- Skips malformed lines with logged warnings

### Sample Usage

```python
from parsers.idx.idx_parser import CrawlerIdxParser

lines = raw_text.splitlines()
records = CrawlerIdxParser.parse_lines(lines)
```

## Downstream Flow

Indexed `FilingMetadata` records are returned by the `FilingMetadataCollector` and passed into:
- `FilingMetadataOrchestrator` (pipeline controller)
- `FilingMetadataWriter` (writes to Postgres table filing_metadata)

This creates a database of filing pointers that can be used for further document retrieval and processing.

## Document Processing Flow

```
Daily crawler.idx file
       │
       ▼
┌──────────────────┐     ┌────────────────────────┐
│CrawlerIdxParser  │────►│FilingMetadata          │
│(Indexer)         │     │(Document Pointers)      │
└──────────────────┘     └────────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │FilingMetadataWriter    │
                         │                        │
                         └────────────┬───────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │Database                │
                         │(filing_metadata table) │
                         └────────────────────────┘
```

## Related Modules
- `models/dataclasses/filing_metadata.py` – pointer dataclass returned by this indexer
- `collectors/crawler_idx/filing_metadata_collector.py` – fetches the .idx file and calls this indexer
- `writers/crawler_idx/filing_metadata_writer.py` – writes the indexed records to the database

## Future Enhancements
- Rename the class to `CrawlerIdxIndexer` to better reflect its role
- Modularize `crawler.idx` download logic into a dedicated `CrawlerIdxDownloader`
- Implement retry or backoff for flaky network responses
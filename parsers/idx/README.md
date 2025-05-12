# IDX Parser Module

This module contains the logic for parsing `crawler.idx` files published daily by the SEC. It is a core component of **Pipeline 1: Filing Metadata Ingestion**.

## Purpose

The `crawler.idx` file is a flat text index of all EDGAR filings submitted on a given day. It contains:
- Company Name
- Form Type
- CIK
- Filing Date
- Filing URL

`CrawlerIdxParser` transforms these flat text records into structured dataclass instances used downstream for ingestion.

## Class: `CrawlerIdxParser`

### Role
- **Classification**: ✅ Parser
- **Input**: `List[str]` (raw lines from `crawler.idx`)
- **Output**: `List[FilingMetadata]` dataclass instances

### Responsibilities
- Locates the header break line in `.idx` (e.g. "-----")
- Extracts each filing’s core fields
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
Parsed `FilingMetadata` records are returned by the `FilingMetadataCollector` and passed into:
- `FilingMetadataOrchestrator` (pipeline controller)
- `FilingMetadataWriter` (writes to Postgres table filing_metadata)

## Related Modules
- `models/dataclasses/filing_metadata.py` – pointer dataclass returned by this parser
- `collectors/crawler_idx/filing_metadata_collector.py` – fetches the .idx file and calls this parser
- `writers/crawler_idx/filing_metadata_writer.py` – writes the parsed records to the database

## Future Enhancements
- Modularize `crawler.idx` download logic into a dedicated `CrawlerIdxDownloader`
- Implement retry or backoff for flaky network responses
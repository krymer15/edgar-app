# downloaders

This module contains classes responsible for downloading content from the SEC EDGAR system. Each downloader is specialized for a particular content type and follows a common interface.

## Core Downloader Classes

- **base_downloader.py**  
  Abstract base class defining the common interface for all downloaders.
  
- **sec_downloader.py**  
  Base implementation for SEC API communication with rate limiting and headers.
  
- **sgml_downloader.py**  
  Downloads and caches SGML/text `.txt` filings with memory and disk caching.

**Note:** The `form4_xml_downloader.py` file has been deprecated and moved to the `archive/` directory as it's not used in current pipelines.

## Class Hierarchy

```
         ┌──────────────┐
         │BaseDownloader│
         └──────┬───────┘
                │
                │
         ┌──────▼───────┐
         │ SECDownloader │
         └──────┬───────┘
                │
                │
         ┌──────▼───────┐
         │SgmlDownloader│
         └──────────────┘
```

## Core Functionality

### SECDownloader

Base implementation with SEC-specific functionality:

```python
downloader = SECDownloader(
    user_agent="MyCompanyBot/1.0",
    request_delay_seconds=0.2
)

html_content = downloader.download_html("https://www.sec.gov/...")
json_data = downloader.download_json("https://www.sec.gov/api/...")
```

Key features:
- Request throttling to comply with SEC guidelines
- Proper User-Agent header configuration
- Error handling and retries
- HTTP and JSON response processing

### SgmlDownloader

Specialized downloader for SGML text files with caching:

```python
downloader = SgmlDownloader(
    user_agent="MyCompanyBot/1.0",
    request_delay_seconds=0.2,
    use_cache=True
)

# Returns a SgmlTextDocument dataclass
sgml_doc = downloader.download_sgml(
    cik="0000123456",
    accession_number="0000123456-25-123456",
    year="2025"
)
```

Key features:
- Multi-level caching (memory and disk)
- Integration with path_manager for standardized file paths
- Returns strongly-typed dataclass objects
- Shared instance can be used across pipeline stages for efficiency
- Consistent URL construction for accession numbers with or without dashes

## Extension for Additional Form Types

The current architecture supports extension in two ways:

1. **Extending SgmlDownloader**: The SgmlDownloader can be enhanced to handle different document types beyond SGML text files. This would be the preferred approach for consistency.

   Example implementation for XML downloading:
   ```python
   def download_xml(self, cik: str, accession_number: str, filename: str) -> XmlDocument:
       url = construct_primary_document_url(cik, accession_number, filename)
       content = self.download_html(url)
       return XmlDocument(cik=cik, accession_number=accession_number, content=content)
   ```

2. **Creating New Specialized Downloaders**: For completely different sources or formats that require special handling, new downloader classes can be implemented:

   ```python
   class XbrlDownloader(SECDownloader):
       def download_xbrl(self, cik: str, accession_number: str, filename: str) -> XbrlDocument:
           # Specialized implementation for XBRL files
           pass
   ```

## Usage in Pipelines

Downloaders are typically instantiated and used by orchestrators:

```python
# In an orchestrator
downloader = SgmlDownloader(
    user_agent=self.user_agent,
    request_delay_seconds=0.1,
    use_cache=self.use_cache
)

# Download a specific filing
sgml_doc = downloader.download_sgml(
    cik=filing.cik,
    accession_number=filing.accession_number
)

# Process the downloaded content
# ...
```

The `Form4Orchestrator` uses the `SgmlDownloader` to download SGML files containing Form 4 data, which are then parsed by the `Form4SgmlIndexer`.
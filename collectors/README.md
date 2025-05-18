# Collectors

Collectors are components responsible for retrieving and collecting data from various sources in the EDGAR data processing system. They serve as the initial stage of each pipeline, fetching raw data that will be processed by downstream components.

## Collector Architecture

All collectors follow a consistent pattern defined by the `BaseCollector` abstract base class:

```python
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    @abstractmethod
    def collect(self, *args, **kwargs):
        """Collect raw filing metadata or references."""
        pass
```

This simple interface ensures all collectors implement a consistent `collect` method, though the specific parameters and return types vary based on the data source.

## Directory Structure

```
collectors/
│
├── base_collector.py            # Abstract base class for all collectors
│
├── crawler_idx/                 # SEC daily index collectors
│   ├── filing_metadata_collector.py   # Pipeline 1: Downloads crawler.idx
│   ├── filing_documents_collector.py  # Pipeline 2: Extracts document metadata
│   └── sgml_disk_collector.py         # Pipeline 3: Downloads SGML files
│
└── submissions_api/             # SEC Submissions API collectors
    └── submissions_collector.py       # Collects company submissions
```

## Collector Types

### Crawler IDX Collectors

The `crawler_idx` collectors form the core of the EDGAR data processing system, implementing the three main pipeline stages:

1. **FilingMetadataCollector** - Downloads and parses the SEC's daily `crawler.idx` file, extracting basic filing metadata (CIK, accession number, form type, date).

2. **FilingDocumentsCollector** - Uses the filing metadata to download SGML files and extract document information (HTML, XML, text files) contained within each filing.

3. **SgmlDiskCollector** - Downloads and saves raw SGML files to disk in a structured directory hierarchy.

See [crawler_idx/README.md](crawler_idx/README.md) for detailed documentation on these collectors.

### Submissions API Collectors

The `submissions_api` collectors work with the SEC's Company Submissions API:

1. **SubmissionsCollector** - Retrieves filing metadata for a specific company by CIK directly from the SEC's JSON API.

See [submissions_api/README.md](submissions_api/README.md) for detailed documentation on these collectors.

## Integration with Other Components

Collectors are used by orchestrators to fetch data, which is then passed to parsers, and finally to writers for persistence:

```
Orchestrator → Collector → (Downloader) → Parser → Writer
```

## Key Design Patterns

### 1. Dependency Injection

Collectors receive their dependencies (downloaders, database sessions) via constructor injection:

```python
class ExampleCollector(BaseCollector):
    def __init__(self, db_session, user_agent, downloader=None):
        self.db_session = db_session
        self.downloader = downloader or SomeDownloader(user_agent=user_agent)
```

This allows for:
- Sharing resources between components (e.g., using the same downloader instance)
- Easier testing through component mocking
- More flexible configuration

### 2. Filtering Options

Most collectors support filtering options to limit the data being collected:

- Date filtering (`target_date`)
- Form type filtering (`include_forms`)
- Record count limiting (`limit`)
- Specific record selection (`accession_filters`)

### 3. Return Types

Collectors typically return structured data in one of two forms:

- Lists of dataclass instances (e.g., `FilingMetadata`, `FilingDocumentRecord`)
- Lists of simple data structures (e.g., dictionaries for the Submissions API)

## Common Usage Patterns

### Pipeline 1: Filing Metadata Collection

```python
from collectors.crawler_idx.filing_metadata_collector import FilingMetadataCollector

collector = FilingMetadataCollector(user_agent="Example/1.0")
metadata = collector.collect(date="2025-05-12", include_forms=["10-K", "8-K"])
```

### Pipeline 2: Document Metadata Collection

```python
from collectors.crawler_idx.filing_documents_collector import FilingDocumentsCollector

collector = FilingDocumentsCollector(db_session=session, user_agent="Example/1.0")
documents = collector.collect(target_date="2025-05-12")
```

### Pipeline 3: SGML File Collection

```python
from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector

collector = SgmlDiskCollector(db_session=session, user_agent="Example/1.0")
filepaths = collector.collect(target_date="2025-05-12")
```

### Submissions API Collection

```python
from collectors.submissions_api.submissions_collector import SubmissionsCollector

collector = SubmissionsCollector(user_agent="Example/1.0")
filings = collector.collect(cik="0001234567", forms_filter=["10-K", "8-K"])
```
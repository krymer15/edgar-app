# Orchestrators

Orchestrators are the central coordinators that wire together different components of the EDGAR data processing system. They manage the end-to-end flow from data collection to persistence.

## Architecture Overview

The orchestration layer is structured around three primary data sources:

1. **Crawler IDX** - Processing the SEC's daily index files
2. **Forms** - Form-specific processing (e.g., Form 4 XML extraction)
3. **Submissions API** - Direct ingestion from the SEC's Company Submissions API

Each data source has dedicated orchestrators that coordinate specialized collectors, parsers, and writers.

## Base Pattern

All orchestrators extend the `BaseOrchestrator` abstract base class:

```python
class BaseOrchestrator(ABC):
    @abstractmethod
    def orchestrate(self, *args, **kwargs):
        """Manage the ingestion flow across collector, downloader, parser, writer."""
        pass
```

This consistent interface ensures all orchestrators follow the same basic pattern:
1. Initialize components (collectors, writers, downloaders)
2. Implement the `orchestrate` method to define the processing flow
3. Provide a `run` method as the public API with additional logging

## Key Design Patterns

### 1. Component Dependency Injection

Orchestrators receive their collaborating components (collectors, downloaders, writers) via constructor injection, allowing for:
- Flexibility in component composition
- Sharing of components between orchestrators (e.g., shared downloaders)
- Easier testing through component mocking

### 2. Meta-Orchestration

The `DailyIngestionPipeline` is a meta-orchestrator that coordinates multiple lower-level orchestrators:
- Controls the execution sequence across multiple pipelines
- Shares resources between pipelines (e.g., downloader instances)
- Manages cross-cutting concerns like error handling and job tracking

### 3. Pipeline Architecture

The system implements three main pipelines for SEC data:
- **Pipeline 1** - Filing metadata from crawler.idx
- **Pipeline 2** - Document metadata extraction from SGML files
- **Pipeline 3** - SGML file download and storage to disk

### 4. Transaction Management

Orchestrators handle database transactions strategically:
- Some use transaction-per-batch for efficiency
- Others use transaction-per-record for fault tolerance
- Error handling preserves transaction boundaries

## Directory Structure

```
orchestrators/
│
├── base_orchestrator.py        # Abstract base class
│
├── crawler_idx/                # SEC daily index orchestrators
│   ├── daily_ingestion_pipeline.py  # Meta-orchestrator for all three pipelines
│   ├── filing_metadata_orchestrator.py  # Pipeline 1
│   ├── filing_documents_orchestrator.py  # Pipeline 2
│   └── sgml_disk_orchestrator.py  # Pipeline 3
│
├── forms/                      # Form-specific orchestrators
│   └── form4_xml_orchestrator.py  # Form 4 specialized processing
│
├── legacy/                     # Older orchestration patterns
│   └── ... 
│
└── submissions_api/            # SEC Submissions API orchestrators
    └── submissions_ingestion_orchestrator.py
```

## Key Orchestrators

### DailyIngestionPipeline

The central coordinator for all crawler.idx-based pipelines:
- Orchestrates Pipelines 1-3 in sequence
- Integrates with form-specific processing
- Implements robust error handling and job tracking
- Supports selective processing via filtering options

### Form4Orchestrator

Specialized orchestrator for Form 4 filings:
- Extracts and processes Form 4 XML from SGML container files
- Works with `Form4SgmlIndexer` to extract embedded XML
- Uses `Form4Writer` to persist complex entity relationships
- Manages document lookup via memory cache → disk → download hierarchy

## Common Code Patterns

### Error Handling

```python
try:
    # Processing logic
    result = self.collector.collect(...)
    self.writer.write(result)
except Exception as e:
    log_error(f"Error during processing: {e}")
    # Optional transaction rollback
    raise  # or handle gracefully
```

### Configuration Management

```python
def __init__(self):
    config = ConfigLoader.load_config()
    self.user_agent = config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
    # Other configuration parameters
```

### Resource Sharing

```python
# Create shared downloader
self.downloader = SgmlDownloader(user_agent=self.user_agent)

# Pass to dependent orchestrators
self.docs_orchestrator = FilingDocumentsOrchestrator(downloader=self.downloader)
self.sgml_orchestrator = SgmlDiskOrchestrator(downloader=self.downloader)
```

## Integration with Scripts

All orchestrators are used via CLI scripts in the `scripts/` directory:
- `scripts/crawler_idx/run_daily_pipeline_ingest.py` - Full pipeline ingestion
- `scripts/crawler_idx/run_daily_metadata_ingest.py` - Pipeline 1 only
- `scripts/crawler_idx/run_daily_documents_ingest.py` - Pipeline 2 only
- `scripts/crawler_idx/run_sgml_disk_ingest.py` - Pipeline 3 only
- `scripts/forms/run_form4_xml_ingest.py` - Form 4 XML extraction only
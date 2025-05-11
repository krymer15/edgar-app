# orchestrators

End-to-end pipelines that wire together crawlers, downloaders, parsers, extractors, and writers:

- **ingestion_orchestrator.py**  
  Crawls → downloads filings → writes raw metadata & documents.

- **parsing_orchestrator.py**  
  - Reads raw docs → parses into chunks → writes parsed models.
  - `ParsingOrchestrator`: loads raw `FilingDocument`, parses, writes `ParsedChunkModel`

- **vectorization_orchestrator.py**  
  - Embeds chunks with an LLM → writes vectors.
  - `VectorizationOrchestrator`: loads `ParsedChunkModel`, calls embedder, writes `FilingVector`

- **summarization_orchestrator.py**  
  - Generates LLM summaries/signals → stores results.
  - `SummarizationOrchestrator`: queries `FilingVector`, reconstructs context, calls `LLMSummarizer`, saves signals or summaries

ABOVE NAMING STILL TBD!!!

```python
class IngestionOrchestrator:
    def __init__(self, crawler, downloader, metadata_writer, document_writer):
        …

    def run(self, date: date):
        for acc in crawler.fetch(date):
            raw_meta = downloader.download_metadata(acc)
            metadata_writer.write(raw_meta)
            for doc in downloader.list_documents(acc):
                downloaded = downloader.download(doc)
                document_writer.write(downloaded)
```                

## 🔁 Usage Pattern Across the Pipeline
| Stage      | Input                           | Output                              |
| ---------- | ------------------------------- | ----------------------------------- |
| Downloader | Metadata row → `FilingDocument` | `RawDocument`                       |
| Cleaner    | `RawDocument`                   | `CleanedDocument`                   |
| Parser     | `CleanedDocument`               | `ParsedDocument` or subclass        |
| Writer     | `ParsedDocument`                | Writes to DB (via adapters)         |
| Embedder   | `ParsedChunk`                   | `FilingVector` (stored in pgvector) |


-------------------
## Key Classes (PREVIOUS VERSION!)

### `DailyIngestionOrchestrator`
- Entry point for batch SGML ingestion via `crawler.idx`.
- Supports:
  - TBD

### `FilingMetadataOrchestrator`
- Handles the ingestion of a `crawler.idx` metadata:
  - TBD

### `FilingDocumentsOrchestrator`
- Handles the ingestion of individual document metadata from `crawler.idx` records:
  - TBD

## Pulling Flattened Exhibit Metadata for Internal Logic
Goal: Allow your internal logic (e.g., parsers, embedders) to retrieve exhibit metadata from Postgres and locate the correct file on disk.

🔄 Recommended Workflow:
1. Query SQLAlchemy ORM:
- Use an ORM model like `ExhibitMetadata` to query the metadata.

2. Convert ORM to @dataclass:
- Use a factory method or `.from_orm()` (if using Pydantic) to convert this record into a `@dataclass` object like `FilingDocument`.

3. Resolve file path:
- Use a centralized `path_manager.py` module:

```python
filepath = path_manager.build_raw_filepath(
    year=2024,
    cik=filing.cik,
    accession_or_subtype=filing.accession_number,
    form_type=filing.form_type,
    filename=filing.filename
)
```

4. Open or parse file:
- The resulting filepath (on your SSD) is then passed to your cleaner/parser modules.

### Example Flow:
```python
from db.orm_models import ExhibitMetadataORM
from models.filing_document import FilingDocument
from utils.path_manager import build_raw_filepath

# 1. Query flattened exhibit metadata
exhibit_record = session.query(ExhibitMetadataORM).filter_by(accession_number="0001234567-25-000001").first()

# 2. Convert to internal dataclass
filing_doc = FilingDocument.from_orm(exhibit_record)

# 3. Resolve path
filepath = build_raw_filepath(
    year=2025,
    cik=filing_doc.cik,
    accession_or_subtype=filing_doc.accession_number,
    form_type=filing_doc.form_type,
    filename=filing_doc.filename
)

# 4. Read or pass to parser
with open(filepath, 'r') as f:
    content = f.read()
```


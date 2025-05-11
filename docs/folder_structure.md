# Folder Structure

```bash
edgar_app/
│
├── config/                   # Global configuration
│   └── app_config.yaml
│   └── config_loader.py
│
├── models/                   
|   └── dataclasses/          # pure Python dataclasses for in-flight logic
│       ├── raw_document.py
│       ├── cleaned_document.py
|       ├── parsed_document.py
│       └── parsed_filing.py  # base class
│
|   └── orm_models/           # SQLAlchemy table mappings
|       ├── filing_metadata.py
|       ├── filing_document.py
|       └── parsed_chunk_model.py
│   └── database.py           # session maker, engine
│
|   └── adapters/             # holds only conversion functions (dataclass ↔ ORM)
|       ├── dataclass_to_orm.py
|       └── orm_to_dataclass.py
│
├── utils/                    # Utility logic
│   ├── path_manager.py       # File path resolver
│   ├── ticker_cik_mapper.py
│   ├── field_normalizer.py
│   └── report_logger.py
│
├── collectors/              # Fetch metadata (Phase 1)
│   └── filing_metadata_collector.py
│
├── downloaders/             # Download full raw files (Phase 2)
│   ├── base_downloader.py
│   ├── sgml_downloader.py
│   ├── html_downloader.py
│   └── xml_downloader.py
│
├── cleaners/                # Strip raw files of style, prep for parsing
│   ├── base_cleaner.py                   # Abstract base, shared utils
│   │
│   ├── sgml/                             # SGML submissions  
│   │   └── sgml_cleaner.py
│   │
│   ├── html/                             # HTML cleanup  
│   │   └── html_cleaner.py
│   │
│   └── xbrl/                             # XBRL cleanup  
│       └── xbrl_cleaner.py
│
├── parsers/                 # Parse raw/cleaned docs to structure
│   ├── base_parser.py                    # Abstract base, shared utils
│   ├── router.py                         # route_parser(form_type) → appropriate parser
│   │
│   ├── sgml/                             # SGML-specific parsing
│   │   ├── sgml_parser.py
│   │   └── sgml_filing_parser_service.py
│   │
│   ├── html/                             # HTML-based filings
│   │   └── html_parser.py
│   │
│   ├── xbrl/                             # XBRL-based filings
│   │   └── xbrl_parser.py
│   │
│   ├── form4/                            # Form 4 (XML)  
│   │   └── form4_parser.py
│   │
│   └── eightk/                           # 8-K (often SGML + Exhibits)
│      └── eightk_parser.py
│
├── writers/                 # Write parsed data to DB
│   ├── base_writer.py                    # Abstract base, shared DB logic
│   │
│   ├── sgml/                             # Parsed SGML chunks → DB  
│   │   └── parsed_sgml_writer.py
│   │
│   ├── documents/                        # FilingDocument ORM writes  
│   │   └── filing_documents_writer.py
│   │
│   ├── form4/                            # Form 4 → specialized table (if any)
│   │   └── form4_writer.py
│   │
│   ├── eightk/                           # 8-K → exhibits table  
│   │   └── eightk_writer.py
│   └── tenk/                             # 10-K → XBRL financials table  
│       └── tenk_writer.py
│
├── embedders/               # Vectorization layer
│   └── openai_embedder.py
│
├── orchestrators/           # Pipeline control (by form or phase)
│   ├── filing_metadata_orchestrator.py
│   ├── filing_documents_orchestrator.py
│   └── form4_orchestrator.py
│
├── scripts/                 # CLI entrypoints and dev scripts
│   ├── run_daily_metadata.py
│   ├── run_form4_xml_ingest.py
│   └── __init__.py
│
├── tests/                   # Unit and integration tests
│   ├── test_path_manager.py
│   ├── test_cli_ingestion.py
│   └── fixtures/
│
└── data/                    # Mounted SSD path (gitignored)
    ├── raw/
    └── processed/
```
- Above we need an `adapters` folder for ORM to Dataclass, and Dataclass to ORM
Central Adapters module:
```bash
safeharbor_edgar_ai/
└── models/
    ├── dataclass/
    └── adapters/
        └── dataclass_to_orm.py
```
In `dataclass_to_orm.py` you’d collect all your conversion functions:

```python
def parsed_doc_to_orm(pd: ParsedDocument) -> FilingDocument: ...
def parsed_chunk_to_orm(pc: ParsedChunk) -> ParsedChunkModel: ...
def filing_to_orm(f: ParsedFiling) -> FilingMetadata: ...
```

Reverse Mapping: `orm_to_dataclass()`
Your orchestrators shouldn’t import SQLAlchemy models directly. Instead, provide adapter functions:

```python
# models/adapters/orm_to_dataclass.py

def metadata_to_header(meta: FilingMetadata) -> FilingHeader:
    return FilingHeader(
        accession_number=meta.accession_number,
        form_type=meta.form_type,
        filing_date=meta.filing_date,
        report_date getattr(meta, "report_date", None),
    )

def document_model_to_raw(doc_model: FilingDocument) -> RawDocument:
    return RawDocument(
        accession_number=doc_model.accession_number,
        cik=doc_model.cik,
        form_type=doc_model.filing.form_type,
        filename=doc_model.filename,
        source_url=doc_model.source_url,
        doc_type=doc_model.source_type,
        source_type=doc_model.source_type,
        is_primary=doc_model.is_primary,
        is_exhibit=doc_model.is_exhibit,
        accessible=doc_model.accessible,
    )
```

--------
## Notes on Design
✅ @dataclass: Ideal for in-memory transport, parsing logic, and LLM prompts.
✅ ORM models: Only used in `writers/` and `collectors/` for DB read/write.
✅ Path Manager: Central resolver so no hardcoded file logic elsewhere.
✅ Separation of Phases: Phase 1 = metadata; Phase 2 = file download; Phase 3 = parsing; Phase 4 = embedding.

## Folder Structure with Specialized Subclasses:

```bash
models/
├── base/
│   ├── filing_document.py       # Base FilingDocument, DownloadedDocument, etc.
│   ├── parsed_filing.py         # Base ParsedFiling. Subclass `ParsedFiling` and group by form in folders
│   └── parsed_chunk.py
│
├── form4/
│   ├── parsed_form4.py          # ParsedForm4 extends ParsedFiling
│   └── xml_models.py            # Optional: XML tag-specific dataclasses
│
├── form10k/
│   ├── parsed_10k.py            # Parsed10K extends ParsedFiling
│   └── xbrl_models.py           # e.g., Revenue, NetIncome from us-gaap tags
│
└── __init__.py
```

### Example (Subclassing `ParsedFiling`)

```python
# models/base/parsed_filing.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedFiling:
    cik: str
    accession_number: str
    form_type: str
    parsed_at: Optional[str] = None  # ISO timestamp
```

```python
# models/form4/parsed_form4.py
from dataclasses import dataclass
from models.base.parsed_filing import ParsedFiling

@dataclass
class ParsedForm4(ParsedFiling):
    issuer_cik: str
    insider_name: str
    transaction_date: str
    shares_acquired: float
    shares_disposed: float
```
Then, conceivably, in a `parsers/form_router.py`:

```python
def route_parser(form_type: str):
    if form_type == "4":
        return Form4Parser()
    elif form_type == "10-K":
        return Xbrl10kParser()
    else:
        raise NotImplementedError(f"No parser available for {form_type}")
```


## Should You Use Pydantic to Convert to Internal Dataclasses?
Short answer: No, not unless you're building a public-facing API layer or need complex validation logic.

🔍 Why not Pydantic here:
- You already use SQLAlchemy ORM — introducing Pydantic for internal use adds overhead and redundancy.
- Pydantic adds runtime validation and serialization, which you don’t typically need when passing already-known-good objects internally between modules like parsers, embedders, and writers.
- Speed: Native @dataclass is faster and simpler, especially for batch workloads like yours.

✅ Recommended:
Use standard Python @dataclass for all internal data modeling. If you ever expose a FastAPI or Flask API later, you can layer Pydantic separately for validation at the boundary.

## Why a Factory Method Instead of `.from_orm()` Pydantic?
- A factory method is a custom class method (typically from_orm(), from_db_model(), or similar) that instantiates a dataclass using an ORM object.
- This gives you full control, keeps it lightweight, and doesn’t require external libraries like Pydantic.
- We implement this through modules in `models/adapters/`.

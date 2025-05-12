# Safe Harbor EDGAR AI App – Dataclass Pipeline Map

This document outlines the key dataclasses used throughout the Safe Harbor EDGAR AI App ingestion, parsing, and embedding pipelines. Each dataclass represents a structured unit of data passed between pipeline stages, ensuring traceability, strong typing, and consistent metadata handling across collectors, downloaders, writers, and parsers.

Reference: https://chatgpt.com/c/681f8e70-c75c-800c-a149-4601f31f0a4f?model=gpt-4o

---

## 🔁 Pipeline Dataclass Map

| Stage          | Input Class           | Output Class           | Description                                                                 |
|----------------|-----------------------|-------------------------|-----------------------------------------------------------------------------|
| Collector      | —                     | `FilingMetadata`        | Extracts CIK, accession, form type, and filing dates from SEC index.       |
| Downloader     | `FilingMetadata`      | `DownloadedDocument`    | Downloads raw SEC content via metadata URL.                                |
| Raw Writer     | `DownloadedDocument`  | `RawDocument`           | Saves raw SGML/HTML/XBRL files to disk.                                    |
| Cleaner        | `RawDocument`         | `CleanedDocument`       | Normalizes HTML content, strips tags, and handles whitespace.              |
| Parser         | `CleanedDocument`     | `ParsedDocument`        | Extracts structured content, segments, and flags from filings.             |
| Chunker        | `ParsedDocument`      | `ParsedChunk`           | Splits large text into embedding-ready segments.                           |
| Embedder       | `ParsedChunk`         | `ParsedChunk` (updated) | Appends vector embeddings for semantic search.                             |
| DB Writer      | All above             | ORM Models              | Maps and stores the dataclasses into SQLAlchemy tables.                    |

---

## 🧱 Core Dataclasses (Defined in `models/dataclasses/`)

### `FilingMetadata`
Used by: **Collector → Downloader → DB Writer**

```python
@dataclass
class FilingMetadata:
    accession_number: str
    cik: str
    form_type: str
    filing_date: date
    filing_url: Optional[str] = None
    period_of_report: Optional[date] = None
    accepted_datetime: Optional[datetime] = None
```
### `DownloadedDocument`
Used by: **Downloader → Raw Writer**

```python
@dataclass
class DownloadedDocument:
    accession_number: str
    cik: str
    form_type: str
    source_url: str
    raw_bytes: bytes
    doc_type: str
    sequence: Optional[int] = None
    is_primary: bool = False
    is_exhibit: bool = False
    content_type: Optional[str] = None
    fetch_timestamp: datetime
```

### `RawDocument`
Used by: `Raw Writer → Cleaner`

```python
@dataclass
class RawDocument:
    accession_number: str
    cik: str
    form_type: str
    filename: str
    local_path: Optional[str]
    source_url: str
    doc_type: str
    is_primary: bool
    is_exhibit: bool
    content_type: Optional[str]
```

### `CleanedDocument`
Used by: `Cleaner → Parser`

```python
@dataclass
class CleanedDocument:
    accession_number: str
    cik: str
    doc_type: str
    local_path: str
    cleaned_text: str
    sequence: Optional[int]
    cleaned_timestamp: datetime
```

### `ParsedDocument`
Used by: `Parser → Chunker`

```python
@dataclass
class ParsedDocument:
    accession_number: str
    cik: str
    form_type: str
    doc_type: str
    sequence: Optional[int]
    text: str
    local_path: Optional[str]
```

### `ParsedChunk`
Used by: `Chunker → Embedder → DB Writer`

```python
@dataclass
class ParsedChunk:
    accession_number: str
    cik: str
    form_type: str
    chunk_id: str
    text: str
    metadata: Dict[str, Optional[str]]
    embedding: Optional[List[float]]
```

## 🧩 Composite Wrappers
These classes group multiple dataclasses into coherent filing-level units:

### Filing
```python
@dataclass
class Filing:
    header: FilingHeader
    company: CompanyInfo
    raw_documents: List[RawDocument]
    parsed_documents: List[ParsedDocument]
    chunks: List[ParsedChunk]
    extracted_metrics: Dict[str, float]
```

### ParsedFiling
```python
@dataclass
class ParsedFiling:
    header: FilingHeader
    company: CompanyInfo
    documents: List[ParsedDocument]
    chunks: List[ParsedChunk]
    extracted_metrics: Dict[str, float]
```

## 🧪 Specialized Subclass Guidance by Pipeline Stage

| Stage      | Specialization Required? | Reason                                                                                  |
| ---------- | ------------------------ | --------------------------------------------------------------------------------------- |
| Downloader | Rarely                   | Only needed for forms like Form 4 XML with unique URL construction.                     |
| Cleaner    | Sometimes                | Varies for forms with unique embedded scripts or formatting (e.g., 10-K vs. 8-K).       |
| Parser     | Frequently               | Core stage for subclassing due to schema differences across forms (e.g., 10-Q, 4, S-1). |
| Writer     | Rarely                   | Use subclass only when writing to non-standard DB schema (e.g., `form4_transactions`).  |
| Embedder   | No                       | Inputs should always be normalized `ParsedChunk`s.                                      |

## 🧬 Folder Design for Parser Subclassing
Each parsers/[type]/ folder should include specialized helpers:

```bash
parsers/
└── html/
    ├── html_parser.py          # Orchestrates logic and maps DOM → dataclasses
    ├── html_utils.py           # Node traversal, tag stripping, cleaning
    ├── html_selectors.py       # Reusable CSS/XPath selectors
    ├── html_models.py          # Section, Table, Link dataclasses
    ├── html_exceptions.py      # Custom exceptions (e.g., MissingElementError)
    ├── html_chunker.py         # Section-by-header splitting for chunking
    └── html_schema.py          # Schema rules: DOM → structured dataclass
```
Replicate this structure in `parsers/sgml/`, `parsers/xbrl/`, etc., to cleanly isolate form-specific logic and make parsers easily swappable.

## ✅ Best Practices
1. Use `dataclass` for all structured intermediates.
- Maintain immutability and type-checking benefits.

2. Preserve `accession_number`, `cik`, and `form_type` across all stages.
-These identifiers unify stages and serve as primary keys in Postgres.

3. Capture SEC sequence order.
Use `sequence: Optional[int]` on document classes.

4. Track provenance and file status.
- Add `source_type`, `is_exhibit`, and `accessible` fields for transparency.

5. Lean on helper modules in `parsers/[form_type]/`.
- Keep your main parser focused on logic orchestration.

6. ORM Models mirror these dataclasses.
- Define your SQLAlchemy tables in `models/orm_models/`.

## 📁 File Tree Reference

```bash
models/
└── dataclasses/
    ├── filing_metadata.py
    ├── filing_document.py
    ├── parsed_document.py
    ├── parsed_chunk.py
    └── raw_document.py
```

Subclasses for parsed forms exist in:
```bash
parsers/forms/
├── form4_parser.py
├── form10k_parser.py
...
```

## 📌 Summary
A disciplined dataclass architecture powers your ingestion pipelines with:

- 🔄 Reusability between pipelines
- 🔒 Data integrity and schema clarity
- ⚙️ Easy subclassing for form specialization
- 🧠 Compatibility with RAG & vector embeddings
- 🏦 Seamless Postgres persistence

This structure ensures long-term scalability and auditability as the Safe Harbor EDGAR AI Platform evolves.

## Summary of benefits
- Consistency & integrity – Every stage has a well-defined schema; no more loose tuples or missing flags.
- Full SEC coverage – You’ll capture sequence numbers, filing vs. period dates, accepted timestamps, and MIME types.
- Scalability – Local paths and timestamps let your writers and downstream analytics know exactly which version they’re operating on.
- Embedding readiness – `ParsedChunk` is the canonical unit for your RAG/pgvector layer.

## Recommendations at a Glance
1. Augment SEC metadata
- `period_of_report: date`
- `accepted_datetime: datetime`
- `sequence: int` and `description: str` on `RawDocument`

2. Strengthen typing
- Use Python `Enum` for ``doc_type`/`source_type`.
- Validate accession formats (e.g. via regex) at ingestion.

3. Optimize for scale
- Add DB indexes on (`filing_date`), (`form_type`), and any new timestamp fields.
- Plan table partitioning if you ingest 10+ years of daily filings.

With those tweaks, you’ll capture the full richness of the SEC’s filing metadata, improve data integrity, and ensure high-performance querying as your “Safe Harbor Edgar AI App” grows.
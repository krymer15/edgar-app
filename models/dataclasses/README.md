# models/dataclasses

# Dataclass Architecture

This module defines the core dataclass models used across the Safe Harbor EDGAR AI Platform. These classes serve as transportable, lightweight data models that flow between stages of each pipeline.

---

## Naming Conventions

Each dataclass adheres to a standardized naming system based on its role in the pipeline:

| Category                   | Suffix/Pattern         | Description                                                                 |
|----------------------------|------------------------|-----------------------------------------------------------------------------|
| **Data Container**         | `*Document`            | Full transport units, often containing raw or cleaned content              |
| **Pointer/Metadata**       | `*Metadata`, `*Ref`    | Lightweight identifiers, filenames, URLs, or basic structured metadata     |
| **Chunked Unit**           | `*Chunk`               | Content split into embedding- or RAG-ready segments                        |
| **Composite/Wrapper**      | `*Filing`              | Groups documents, chunks, and extracted metrics for full filing context    |
| **Form-Specific Subclass** | `Form10K*`, etc.       | Specialized versions of base classes for parsing or interpretation         |

---

## Examples

### Pointer Example – `FilingMetadata`

```python
@dataclass
class FilingMetadata:
    accession_number: str
    cik: str
    form_type: str
    filing_date: date
    filing_url: Optional[str] = None
```

- Used as an identifier and metadata reference
- Returned from `CrawlerIdxParser.parse_lines()`
- Written to the `filing_metadata` database table
- Not intended to carry full filing content

### Container Example – `RawDocument`, `ParsedDocument`

```python
@dataclass
class RawDocument:
    accession_number: str
    cik: str
    content_bytes: bytes
    filetype: str
```
- Used to carry full document payloads (e.g., SGML, HTML, or XML)
- Passed to parsing or cleaning stages

## Folder Structure Guidance

| Folder                | What it Should Contain                                                  |
| --------------------- | ----------------------------------------------------------------------- |
| `models/dataclasses/` | All pipeline-agnostic dataclass models (raw, parsed, metadata, chunked) |
| `models/orm_models/`  | SQLAlchemy ORM mappings (Postgres schema alignment)                     |
| `models/adapters/`    | Conversion logic between dataclass ↔ ORM                                |
| `models/schemas/`     | Pydantic or API-facing schemas (if added)                               |

## Best Practices
- Pointer classes should remain lightweight and immutable during pipeline runs.
- Transport containers (`*Document`) may be large; avoid passing them unless required.
- Dataclasses should only contain `str`, `int`, `date`, `Optional`, or other dataclasses—not ORM instances.
- Use `UUID` or `accession_number` consistently for linking between stages.



--- Old documentation below ---

Pure Python `@dataclass` definitions for in-memory pipeline objects:

- **RawDocument**  
  Metadata + raw text before cleaning.
- **CleanedDocument** *(optional)*  
  Tag-stripped text ready for parsing.
- **ParsedDocument**  
  Structured representation of each document.
- **ParsedChunk**  
  Granular text segments for embedding/vectorization.
- **FilingHeader**  
  Core metadata (accession, dates, form type).
- **CompanyInfo**  
  Company identifier data (CIK, ticker, SIC).
- **ParsedFiling**  
  Aggregate dataclass tying header, company, all docs, chunks, and extracted metrics.

## What goes into raw_documents:
Each `RawDocument` in that list represents one of the files you pulled from SEC:

| doc\_type             | Example URL                            | RawDocument.doc\_type |
| --------------------- | -------------------------------------- | --------------------- |
| **Index page**        | `…/0000320193-22-000108-index.html`    | `"index_html"`        |
| **Primary SGML/Text** | `…/0000320193-22-000108.txt`           | `"sgml"` or `"text"`  |
| **Exhibit**           | `…/EX-99.1.html` or other exhibit file | `"exhibit_html"`      |
| **XBRL**              | `…/FilingXML.xml`                      | `"xbrl"`              |

You’ll feed all of these into your parsers:
- The SGML parser will look at `.txt` and pull header + metadata + initial chunks.
- The HTML parser can split the index page or exhibit HTML into sections.
- The XBRL parser will pick up structured line‐items out of the XML.

### Mapping to parsed_documents
For each `RawDocument`, your parsers emit one or more `ParsedDocument` objects:
- `ParsedDocument` preserves the key metadata (filename, type, flags) and captures the cleaned text you actually want to work with.
- Your ParsedDocument list will therefore include entries like:
    - One for the SGML/text blob (with `is_primary=True`)
    - One per exhibit (with `is_exhibit=True`)
    - Optional ones from index HTML if you parse MD&A blocks directly off it
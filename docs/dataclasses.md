
# Dataclasses

## `RawDocument`
```python
# models/dataclass/raw_document.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class RawDocument:
    accession_number: str
    cik: str
    form_type: str                # e.g. “10-K”, “8-K”, “4”
    filename: str
    source_url: str
    doc_type: str                 # “sgml”, “index_html”, “xbrl”, “exhibit_html”
    source_type: str              # usually same as doc_type, but you can use “inferred” etc.
    is_primary: bool = False      # True for the main filing text
    is_exhibit: bool = False
    accessible: bool = True       # SEC sometimes flags exhibits as non-public
```
Above:
- `form_type` lets downloaders choose the right parser or downstream logic.
- `doc_type` vs `source_type`: you can collapse these if you never need both; otherwise, use `doc_type` for format and `source_type` for origin (e.g., “crawler”, “backfill”, “user-uploaded”).

## `CleanedDocument`
If you have distinct “cleaning” (strip HTML, remove tags) and “parsing” (extract header, sections), it’s helpful to separate:

```python
@dataclass
class CleanedDocument:
    accession_number: str
    cik: str
    form_type: str
    filename: str
    cleaned_text: str             # after tag‐stripping, normalization
    doc_type: str
    is_primary: bool = False
    is_exhibit: bool = False
```

Pipeline flow:
`RawDocument` → cleaner → `CleanedDocument` → parser → `ParsedDocument` & `ParsedChunk`

This makes it obvious when you’ve applied your generic cleaning rules versus domain‐specific parsing.

```python
# models/dataclass/filing_header.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class FilingHeader:
    accession_number: str
    form_type: str
    filing_date: date
    report_date: Optional[date] = None
```

```python
# models/dataclasses/filing.py
@dataclass
class Filing:
    header: FilingHeader                # accession, dates, form type
    company: CompanyInfo                # CIK, ticker, name
    raw_documents: List[RawDocument]    # every URL you fetched
    parsed_documents: List[ParsedDocument]  # cleaned+split versions of each raw doc
    chunks: List[ParsedChunk]           # granular text pieces for embeddings/search
    extracted_metrics: Dict[str, float] # any ratios or signals you’ve pulled out
```

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

```python
# models/dataclass/company_info.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CompanyInfo:
    cik: str
    name: str
    ticker: Optional[str] = None
```

```python
# models/dataclass/parsed_document.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedDocument:
    cik: str
    accession_number: str
    form_type: str
    filename: str
    description: Optional[str]
    source_url: str
    source_type: str = "sgml"
    is_primary: bool = False
    is_exhibit: bool = False
    accessible: bool = True
```

```python
# models/dataclass/parsed_chunk.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedChunk:
    chunk_id: str
    accession_number: str
    text: str
    section: Optional[str]
    page_number: Optional[int]
```

```python
# models/dataclass/parsed_filing.py
from dataclasses import dataclass, field
from typing import List, Dict
from .company_info import CompanyInfo
from .filing_header import FilingHeader
from .parsed_document import ParsedDocument
from .parsed_chunk import ParsedChunk

@dataclass
class ParsedFiling:
    header: FilingHeader
    company: CompanyInfo
    documents: List[ParsedDocument] = field(default_factory=list)
    chunks: List[ParsedChunk] = field(default_factory=list)
    extracted_metrics: Dict[str, float] = field(default_factory=dict)
```

## Other Specialized Classes

- Exhibits: if you need to attach extra exhibit-specific metadata (e.g. exhibit number, accessible flag), you could have:

```python
@dataclass
class ExhibitInfo:
    accession_number: str
    exhibit_id: str         # "EX-99.1", "EX-10.4"
    description: str
    url: str
```

Fiscal vs Calendar Periods: only introduce a `FiscalPeriod` class if you have multiple calendar definitions per company year. Otherwise you can store `period_end_date: date` on each `FinancialStatement`.

# Persistence Models (`models/orm`)
Your SQLAlchemy classes mirror the dataclasses for storage:

```python
# filing_metadata.py
from sqlalchemy import Column, String, Date, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from models.base import Base

class FilingMetadata(Base):
    __tablename__ = "filing_metadata"

    accession_number = Column(String, primary_key=True)
    cik              = Column(String, nullable=False, index=True)
    form_type        = Column(String, nullable=False)
    filing_date      = Column(Date)
    filing_url       = Column(String)
    created_at       = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at       = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    documents = relationship("FilingDocument", back_populates="filing")
```

```python
# filing_document.py  (you already have this)
# … [as in your attached file]
```

```python
# parsed_chunk_model.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from models.base import Base
from uuid import uuid4

class ParsedChunkModel(Base):
    __tablename__ = "parsed_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    accession_number = Column(String, ForeignKey("filing_metadata.accession_number"), nullable=False)
    chunk_id         = Column(String, nullable=False, unique=True)
    text             = Column(Text, nullable=False)
    section          = Column(String)
    page_number      = Column(String)
    embedding        = Column(ARRAY(Float))  # or use pgvector type
```

```python
# filing_vector.py
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from models.base import Base
from uuid import uuid4

class FilingVector(Base):
    __tablename__ = "filing_vectors"

    id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("parsed_chunks.id"), nullable=False)
    vector   = Column(Vector(1536), nullable=False)
```

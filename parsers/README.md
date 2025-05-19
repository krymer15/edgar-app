# Parsers

Parsers transform raw or cleaned text into structured objects. This directory contains all parsing logic organized by document type and purpose.

## Architecture Overview

The parsing system follows a layered approach with a conceptual distinction between **Indexers** and **Parsers**:

1. **Indexers**: Extract document blocks, metadata, and pointers from container files
   - Located in `indexers/` subfolders (e.g., `sgml/indexers/`, `idx/`, etc.)
   - Primarily concerned with locating and extracting documents
   - Return document metadata and pointers rather than fully parsed content

2. **Parsers**: Process specific document types and extract structured data
   - Located in format-specific directories (e.g., `forms/`, future: `html/`, `xbrl/`)
   - Responsible for detailed content extraction and structuring
   - Convert raw content into structured dataclass objects

This separation ensures:
- Clear responsibility boundaries between document extraction and content parsing
- Reusable format-specific logic across pipelines
- Clean separation of concerns
- Specialized handling for different document types

### Natural Ambiguities in SEC Filing Processing

SEC filings have inherent format complexities that can blur the distinction between indexing and parsing:

1. **Embedded Formats**: SGML container files (.txt) often contain embedded XML, HTML, or other formats.
   - Example: Form 4 filings embed structured XML inside SGML containers
   - This requires a multi-stage approach with both SGML indexing and XML parsing

2. **Format Overlap**: Format classifications aren't always distinct.
   - XBRL is a specialized subset of XML, making category distinction challenging
   - Some indexers (like Form4SgmlIndexer) must do preliminary parsing to extract entity information before deep parsing

3. **Dual-Role Components**: Some components perform both indexing and preliminary parsing.
   - Form-specific SGML indexers extract basic metadata from SGML headers AND extract XML for full parsing
   - The boundary between indexing and parsing blurs when extraction requires content understanding

For this reason, the codebase structure represents the ideal separation, while some components might perform both duties. The code documentation in each module clarifies its specific responsibilities.

## Directory Structure

```
parsers/
├── __init__.py
├── base_parser.py                 # Abstract parser interface
├── filing_parser_manager.py       # Router that dispatches to correct parser
├── embedded_doc_parser.py         # (Submissions API) Processes embedded documents
├── exhibit_parser.py              # (Submissions API) Cleans and processes HTML exhibits
├── index_page_parser.py           # (Submissions API) Extracts links from index.html pages
│
├── forms/                         # Form-specific parsers
│   ├── README.md
│   ├── form4_parser.py            # XML Form 4 parser
│   ├── form8k_parser.py           # 8-K current event parser
│   ├── form10k_parser.py          # Annual report parser
│   └── ...
│
├── sgml/                          # SGML document processing
│   └── indexers/                  # SGML document extraction & indexing
│       ├── README.md
│       ├── sgml_document_indexer.py
│       ├── sgml_indexer_factory.py
│       └── forms/                 # Form-specific SGML indexers
│           ├── README.md
│           └── ...
│
├── idx/                           # IDX file processing
│   ├── README.md
│   └── idx_parser.py              # Crawler.idx indexer
│
├── html/                          # HTML-specific parsers (placeholder)
│   └── README.md
│
├── utils/                         # Shared parsing utilities
│   ├── README.md               # Utils documentation
│   └── parser_utils.py         # Standardized output creation
│
└── xbrl/                          # XBRL document processing (placeholder)
```

## Core Components

### Base Parser

All parsers inherit from the [`BaseParser`](./base_parser.py) abstract base class:

```python
class BaseParser(ABC):
    @abstractmethod
    def parse(self, *args, **kwargs):
        """Parse raw filings into structured clean outputs."""
        pass
```

### Indexers vs. Parsers

#### Indexers
- **SGML Indexers** ([`sgml/indexers/`](./sgml/indexers/)): Extract `<DOCUMENT>` blocks from SGML filings
- **IDX Parser** ([`idx/idx_parser.py`](./idx/idx_parser.py)): Parses filing metadata from daily IDX files

#### Parsers
- **Form Parsers** ([`forms/`](./forms/)): Extract data from specific SEC form types
- **HTML Parsers** (future, [`html/`](./html/)): Process HTML documents

### Submissions API Components

The following components are primarily used in the Submissions API pipeline:
- [`ExhibitParser`](./exhibit_parser.py): Cleans HTML exhibits
- [`IndexPageParser`](./index_page_parser.py): Extracts links from index pages
- [`EmbeddedDocParser`](./embedded_doc_parser.py): Handles embedded documents

### Filing Parser Manager

The [`FilingParserManager`](./filing_parser_manager.py) routes filing content to the appropriate parser:

```python
parser_manager = FilingParserManager()
parsed_data = parser_manager.route(
    form_type="4", 
    content=xml_content,
    metadata={
        "accession_number": "0001234567-25-000123",
        "cik": "0001234567",
        "filing_date": "2025-01-15"
    }
)
```

## Document Processing Flow

The document processing follows this general flow:

```
Raw Container File (SGML/IDX)
      ↓
Indexer → Extract document blocks/pointers
      ↓
Document Selector → Select primary document
      ↓
Format-Specific Parser → Process specific document format
      ↓
Form-Specific Parser → Extract form-specific data
      ↓
Structured Data Output → Ready for database writers
```

## Sample Processing Flows

### Crawler IDX Processing Flow

1. **IDX Indexing Layer**
   - `CrawlerIdxParser` extracts filing metadata from the daily IDX file
   - Returns a list of `FilingMetadata` objects

2. **Pipeline Processing**
   - Records are processed by the `FilingMetadataOrchestrator`
   - Metadata is written to the database by `FilingMetadataWriter`

### Form 4 Processing Flow

1. **SGML Indexing Layer**
   - `SgmlDocumentIndexer` extracts document blocks from SGML `.txt` files
   - Form-specific indexer may extract embedded XML content

2. **Form Parsing Layer**
   - `Form4Parser` processes the extracted XML content
   - Extracts issuer, owner, and transaction data

3. **Output Creation**
   - Parser creates structured output with standardized fields
   - Includes entity data objects ready for database insertion

## Parser Module Organization

For complex format-specific parsers (like HTML or XBRL), breaking functionality into dedicated modules improves maintainability. A typical format-specific parser directory should be organized as:

```
parsers/
└── html/
    ├── __init__.py
    ├── html_parser.py          # Main parsing entrypoint/class
    ├── html_utils.py           # DOM-traversal helpers, text normalization, safe extraction
    ├── html_selectors.py       # Centralized CSS/XPath selector definitions for common elements
    ├── html_models.py          # Dataclasses for HTML-specific constructs (e.g. Section, Table, Link)
    ├── html_exceptions.py      # Custom exceptions (e.g. MissingElementError, ValidationError)
    ├── html_chunker.py         # Logic to split HTML into semantic chunks (e.g. by header tags)
    └── html_schema.py          # Mapping rules for converting raw DOM → your dataclasses
```

### Module Responsibilities

- **html_parser.py**: Main class that orchestrates the parsing process, staying focused on high-level flow rather than details
  
- **html_utils.py**: Contains low-level routines for DOM manipulation and text processing
  ```python
  # Example functions:
  def extract_node_text(node, selector): ...  # Get all text under a specific node
  def strip_inline_styles(html_content): ...  # Remove CSS styles
  def normalize_whitespace(text): ...        # Standardize spacing and line breaks
  ```

- **html_selectors.py**: Keeps all CSS/XPath strings in one place, making it easier to update when the SEC tweaks their templates
  ```python
  # Example selectors:
  SECTION_TITLE = "//h2"
  SECTION_BODY = "//div[@class='body']"
  TABLE_FINANCIALS = "//table[contains(@class, 'financials')]"
  ```

- **html_models.py**: Defines small dataclasses specific to the format
  ```python
  @dataclass
  class HtmlSection:
      title: str
      body: str
      
  @dataclass
  class HtmlTable:
      headers: Sequence[str]
      rows: Sequence[Sequence[str]]
  ```

- **html_exceptions.py**: Lets you raise meaningful errors and catch them up the chain
  ```python
  class MissingElementError(Exception):
      """Raised when a required HTML element isn't found"""
      
  class ValidationError(Exception):
      """Raised when extracted content fails validation"""
  ```

- **html_chunker.py**: Handles breaking a large document into semantic units for processing
  ```python
  def chunk_sections(dom):
      """Split document into sections based on headers"""
      
  def chunk_paragraphs(section):
      """Split a section into paragraphs"""
  ```

- **html_schema.py**: Defines "rules" or mappings for transforming raw DOM to structured data
  ```python
  MAPPING_RULES = {
      "document_title": {"selector": "//h1", "target_field": "title"},
      "financial_tables": {"selector": "//table[@class='financials']", "processor": "process_table"}
  }
  ```

### Implementation Pattern

With these helpers in place, the main parser can stay lean and focused on orchestration:

```python
from .html_utils import extract_node_text
from .html_selectors import SECTION_TITLE, SECTION_BODY
from .html_models import HtmlSection
from .html_exceptions import MissingElementError
from .html_chunker import chunk_sections

class HtmlParser(BaseParser):
    def parse(self, cleaned_doc: CleanedDocument) -> ParsedDocument:
        dom = self._to_dom(cleaned_doc.content)
        
        # Extract key components using specialized modules
        title = extract_node_text(dom, SECTION_TITLE) or raise MissingElementError(...)
        body = extract_node_text(dom, SECTION_BODY)
        sections = chunk_sections(dom)
        
        return ParsedDocument(sections=sections, title=title, ...)
```

### Applying to Other Format Types

The same module organization pattern should be followed in other format-specific directories like `parsers/sgml/`, `parsers/xbrl/`, or any other specialized parser. This approach ensures:

1. The main parser stays focused on orchestration
2. Helper modules handle specialized concerns
3. Code remains testable and maintainable
4. Related functionality is grouped together
5. Updates to format patterns (like SEC template changes) only affect one file

## Development Guidelines

1. **Indexer vs. Parser Responsibilities**
   - **Indexers**: Focus on document extraction and metadata
   - **Parsers**: Focus on content analysis and structured data extraction
   - Place indexers in `indexers/` subfolders within format directories

2. **Standardized Output**
   - Use consistent output structure across all components
   - Include metadata, content type, and parsed data fields
   - Handle errors gracefully with informative error messages

3. **Testing with Fixtures**
   - Use real sample data for development and testing
   - Store fixtures in appropriate locations:
     - Test fixtures: `/tests/fixtures/`
     - Development fixtures: `/data/raw/fixtures/`
   - Use fixture loader utilities when available

4. **Modular Design**
   - Keep parser classes focused on orchestration
   - Delegate specific concerns to dedicated helper modules
   - Centralize selectors and extraction logic for easier maintenance
   - Create reusable utilities that can be shared across parsers

5. **Shared Utilities**
   - Use the [`parser_utils.py`](./utils/parser_utils.py) module for common functionality
   - Create standardized outputs with `build_standard_output()`
   - Refer to [utils/README.md](./utils/README.md) for documentation on available utilities

## Related Components

- [Orchestrators](../orchestrators/): Coordinate parsing, downloading, and writing
- [Writers](../writers/): Persist parsed data to database
- [Models](../models/): Data structures used by parsers
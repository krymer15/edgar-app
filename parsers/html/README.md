# HTML Parser Components

This directory is intended to house HTML-specific parsing utilities for processing SEC filings that appear in HTML format.

## Parsers vs. Indexers

In this codebase, there is a critical distinction between **Parsers** and **Indexers**:

- **Parsers**: Process specific document types and extract structured data. They transform raw content into rich structured objects with meaningful fields.
- **Indexers**: Extract document blocks, metadata, and pointers from container files. They **locate and identify** content without processing its full semantics.

The HTML components in this directory are intended to be parsers that interpret the content of HTML documents after they have been identified and extracted by indexers.

## Current HTML Processing Components

Currently, the HTML parsing functionality is implemented directly in top-level files under the Submissions API pipeline:

- [`ExhibitParser`](../exhibit_parser.py): Cleans and processes HTML exhibits, removing tables and tagging headers.
- [`IndexPageParser`](../index_page_parser.py): Extracts document links from index.html pages.
- [`EmbeddedDocParser`](../embedded_doc_parser.py): Handles embedded HTML documents within filings.

## Future HTML Parser Structure

As the codebase continues to evolve, this directory will be populated with specialized HTML parsers for various filing components. Following best practices for complex format parsers, the directory structure should look like:

```
html/
├── __init__.py
├── html_parser.py          # Main parsing entrypoint/class
├── html_utils.py           # DOM-traversal helpers, text normalization
├── html_selectors.py       # CSS/XPath selector definitions
├── html_models.py          # Dataclasses for HTML-specific constructs
├── html_exceptions.py      # Custom exceptions
├── html_chunker.py         # Logic to split HTML into semantic chunks
└── html_schema.py          # Mapping rules for DOM → dataclasses
```

### Module Responsibilities

- **html_parser.py**: Main entry point that orchestrates the parsing process
- **html_utils.py**: Low-level utilities for DOM manipulation, text cleaning, and normalization
- **html_selectors.py**: Centralized CSS/XPath selectors for common elements (makes it easier to update when SEC changes formats)
- **html_models.py**: Dataclasses for HTML-specific constructs:
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
- **html_exceptions.py**: Custom exception types (e.g., `MissingElementError`, `ValidationError`)
- **html_chunker.py**: Logic for splitting HTML into semantic chunks (by headers, sections, etc.)
- **html_schema.py**: Mapping rules for transforming DOM elements to structured data

This organization keeps the main parser class focused on orchestration with specialized modules handling specific concerns, making the code more maintainable and testable.

## HTML Parsing Techniques

When implementing HTML parsers, consider these techniques:

1. **Use lxml for robust parsing**: The lxml library provides efficient, standards-compliant parsing.
2. **XPath for targeted extraction**: Use XPath expressions to extract specific elements.
3. **Clean text content**: Remove redundant whitespace, normalize line breaks.
4. **Handle encoding issues**: Convert between string and bytes representations as needed.
5. **Preserve semantic structure**: Tag or mark significant sections for downstream processing.

## Document Processing Flow

The HTML parsing components fit into the document processing flow after SGML indexing:

```
SgmlTextDocument (.txt file from EDGAR)
       │
       ▼
┌──────────────────┐     
│SgmlDocumentIndexer│     
└──────┬───────────┘     
       │ (extracts HTML documents)              
       │                               
       ▼                              
┌──────────────────┐    
│HTML Parser       │ <- Future components in this directory
│                  │    (Form-specific HTML parsing)
└──────┬───────────┘    
       │
       ▼
┌──────────────────┐
│Structured Data   │
│                  │
└──────────────────┘
```

## Implementation Example

With the modular approach, a main HTML parser might look like this:

```python
from parsers.base_parser import BaseParser
from .html_utils import extract_node_text
from .html_selectors import SECTION_TITLE, SECTION_BODY
from .html_models import HtmlSection
from .html_exceptions import MissingElementError
from .html_chunker import chunk_sections
from lxml import html

class HtmlParser(BaseParser):
    def __init__(self, accession_number: str, cik: str, filing_date: str):
        self.accession_number = accession_number
        self.cik = cik
        self.filing_date = filing_date
        
    def parse(self, html_content: str) -> dict:
        try:
            # Parse HTML content
            tree = html.fromstring(html_content)
            
            # Extract title using centralized selector
            title = extract_node_text(tree, SECTION_TITLE)
            if not title:
                raise MissingElementError("Could not find title element")
                
            # Extract body text
            body = extract_node_text(tree, SECTION_BODY)
            
            # Break into semantic sections
            sections = chunk_sections(tree)
            
            # Create structured output
            return {
                "parsed_type": "html_document",
                "parsed_data": {
                    "title": title,
                    "body": body,
                    "sections": sections
                },
                "content_type": "html",
                "accession_number": self.accession_number,
                "cik": self.cik,
                "filing_date": self.filing_date
            }
        except Exception as e:
            return {
                "parsed_type": "html_document",
                "error": str(e)
            }
```

This approach keeps the main parser focused on high-level orchestration while delegating specific concerns to specialized modules.

## Related Components

- [Form-Specific Parsers](../forms/)
- [SGML Indexers](../sgml/indexers/) (Extract documents before parsing)
- [Exhibit Parser](../exhibit_parser.py) (Currently part of Submissions API)
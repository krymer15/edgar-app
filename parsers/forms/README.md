# Form-Specific Parsers

This directory contains specialized parsers that handle specific SEC form types. Each parser implements form-specific logic to extract structured data from the raw content of a particular form type.

## Parsers vs. Indexers

In this codebase, there is a critical distinction between **Parsers** and **Indexers**:

- **Parsers**: Process specific document types and extract structured data. They transform raw content into rich structured objects with meaningful fields.
- **Indexers**: Extract document blocks, metadata, and pointers from container files. They **locate and identify** content without processing its full semantics.

Form parsers in this directory are true parsers - they interpret and extract meaningful data from specific form content types (XML, HTML, text) after indexers have identified and extracted the relevant documents.

## Architecture

All form parsers:
1. Inherit from the [`BaseParser`](../base_parser.py) abstract base class
2. Implement the `parse()` method to process content specific to their form type
3. Are designed to work with specific content types (XML, HTML, text)
4. Return standardized output dictionaries with consistent structure

## Router System

Form parsers are managed and dispatched by the [`FilingParserManager`](../filing_parser_manager.py), which:
- Maintains a registry of form types to parser classes
- Normalizes form type strings for consistent matching
- Instantiates the appropriate parser with metadata
- Routes filing content to the correct parser instance

```python
# Example usage
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

## Form Parsers

### Form 4 Parser (`form4_parser.py`)

Processes ownership transaction XML content from Form 4 filings, extracting:
- Issuer information (company being reported on)
- Reporting owner details (insiders filing the form)
- Non-derivative transaction data (direct stock transactions)
- Derivative transaction data (options, warrants, etc.)
- Relationship information between issuers and owners
- Footnotes and additional references

Key features:
- Creates entity data objects for direct use in writers
- Handles both direct and indirect ownership
- Classifies entity types (person vs. company)
- Processes multiple reporting owners in a single filing
- Supports both "1" and "true" string values for relationship flags (is_director, is_officer, etc.)
- Extracts footnote references for both derivative and non-derivative transactions using multiple extraction strategies
- Captures footnotes from various locations in the XML structure (direct elements, attributes, and nested elements)
- Comprehensive footnote ID mapping for creating accurate reference links between transactions and their footnotes
- Uses [`parser_utils.build_standard_output()`](../utils/parser_utils.py) for consistent output format

### Form 8-K Parser (`form8k_parser.py`)

Processes current event report filings (Form 8-K), extracting:
- Item codes (e.g., "2.02" for Results of Operations)
- Summary of the filing content
- Handles primarily text-based content

### Form 10-K Parser (`form10k_parser.py`)

Processes annual reports, extracting:
- Financial statement data
- Company overview information
- Risk factors and management discussion
- Optimized for HTML or XBRL content

### Other Form Parsers

- **Form 3 Parser** (`form3_parser.py`): Initial ownership filings
- **Form S-1 Parser** (`forms1_parser.py`): Registration statements for new securities

## Document Processing Flow

The place of form parsers in the document processing flow:

```
Raw Document Source (SGML/HTML/XML)
      │
      ▼
Indexer (e.g., SgmlDocumentIndexer)
      │
      ▼
Document Extraction
      │
      ▼
┌─────────────────────┐
│Form-Specific Parser │ <- We are here (forms/*.py)
│                     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│Structured Data      │
│Output               │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│Database Writer      │
│                     │
└─────────────────────┘
```

## Extending the System

To add support for a new form type:

1. Create a new form parser class in this directory:
```python
# parsers/forms/form10q_parser.py
from parsers.base_parser import BaseParser

class Form10QParser(BaseParser):
    def __init__(self, accession_number: str, cik: str, filing_date: str):
        self.accession_number = accession_number
        self.cik = cik
        self.filing_date = filing_date
        
    def parse(self, content: str) -> dict:
        # Form-specific parsing logic here
        return {
            "parsed_type": "form_10q",
            "parsed_data": { /* extracted data */ },
            "content_type": "html"  # or other content type
        }
```

2. Register the new parser in `filing_parser_manager.py`:
```python
from parsers.forms.form10q_parser import Form10QParser

# In FilingParserManager.__init__
self.registry = {
    # Existing parsers...
    "10Q": Form10QParser(),
    "FORM 10-Q": Form10QParser(),
}
```

## Best Practices

1. **Single Responsibility**: Each parser should handle only one form type
2. **Standard Output**: Use consistent output structure across all parsers
3. **Proper Error Handling**: Always handle parsing exceptions gracefully
4. **Content Type Awareness**: Design parsers for specific content types (XML, HTML, text)
5. **Entity Creation**: When appropriate, create entity data objects ready for database writers
6. **Clear Boundary**: Focus on content interpretation, not document extraction (which is handled by indexers)
7. **Standard Output Format**: Use [`parser_utils.build_standard_output()`](../utils/parser_utils.py) to ensure consistent output structure

## Related Components

- [Form-Specific Orchestrators](../../orchestrators/forms/)
- [Form-Specific Writers](../../writers/forms/)
- [SGML Indexers](../sgml/indexers/) (Extract documents before parsing)
- [Parsing Utilities](../utils/parser_utils.py)
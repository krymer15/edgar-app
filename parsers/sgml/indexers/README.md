# SGML Document Indexers

This folder contains logic for *indexing* SGML `.txt` submission files retrieved from EDGAR. SGML is the primary format used by the SEC EDGAR system for submission files, containing both metadata in the header sections and embedded document content.

## Indexers vs. Parsers

In this codebase, there is a critical distinction between **Indexers** and **Parsers**:

- **Indexers**: Extract document blocks, metadata, and pointers from container files. They **locate and identify** content without processing its full semantics.
- **Parsers**: Process specific document types and extract structured data. They transform raw content into rich structured objects.

SGML Indexers are specifically responsible for breaking apart SGML container files and identifying the documents within them, not for interpreting the full content of those documents.

## Architecture Overview

The SGML indexing system follows a factory pattern with a base indexer class and specialized form-specific indexers:

```
                   ┌────────────────────┐
                   │ SgmlIndexerFactory │
                   └─────────┬──────────┘
                             │
                             │ creates
                             ▼
                   ┌────────────────────┐
                   │ SgmlDocumentIndexer │◄────┐
                   └─────────┬──────────┘     │
                             │                │
                             │ extends        │
                             ▼                │
                   ┌────────────────────┐     │ registers
                   │  Form-Specific     │     │
                   │     Indexers       │─────┘
                   └────────────────────┘
```

### Key Components

1. **SgmlDocumentIndexer** ([sgml_document_indexer.py](sgml_document_indexer.py))
   - Base indexer class for all SGML document types
   - Handles general SGML document structure parsing
   - Extracts document metadata and identifies embedded content
   - Implements heuristics for primary document selection
   - Returns `FilingDocumentMetadata` objects for each document

2. **SgmlIndexerFactory** ([sgml_indexer_factory.py](sgml_indexer_factory.py))
   - Factory class for creating appropriate indexers based on form type
   - Maintains a registry of specialized indexers
   - Falls back to the base indexer for unsupported form types
   - Normalizes form types for consistent matching (e.g., "Form 4", "4", "form-4" all map to "4")

3. **Form-Specific Indexers** ([forms/](forms/))
   - Specialized indexers for specific form types
   - Extend the base indexer with form-specific extraction logic
   - Currently implemented:
     - `Form4SgmlIndexer`: Specialized for Form 4 filings

## Role in Pipeline

SGML indexers are a critical bridge in the processing pipeline. They operate on raw `.txt` content (wrapped in `SgmlTextDocument`) to:

1. Extract document metadata from SGML headers
2. Identify and categorize embedded documents (primary, exhibits, etc.)
3. Extract embedded content (XML, HTML) for further processing by specialized parsers
4. Generate structured pointers (`FilingDocumentMetadata`) to all components

This is specifically the **first phase** of document processing, focused on extraction and identification, not on full content interpretation.

## Factory Pattern Usage

The SGML indexing system uses a factory pattern to create the appropriate indexer:

```python
# Create the appropriate indexer for a filing
indexer = SgmlIndexerFactory.create_indexer(
    form_type="4",
    cik="0000123456",
    accession_number="0000123456-25-000123"
)

# Index the SGML content
documents = indexer.index_documents(sgml_text_content)
```

This factory approach allows:
- Easy extension for new form types
- Consistent interface for all form types
- Fallback to general indexing for unsupported forms

## Primary Document Selection

A key responsibility of SGML indexers is to identify the "primary" document within a filing. This determination is made using a prioritized rule-based approach:

1. HTML files with sequence number 1
2. Form-named HTML files (e.g., containing "10-k", "8-k", etc. in filename)
3. Any HTML file
4. XML files

This ensures that the most relevant document is marked for display or further processing.

## Common Indexing Functionality

### Base SGML Indexer

The `SgmlDocumentIndexer` class performs these core functions:

- Splits SGML content into document sections using `<DOCUMENT>` tags
- Extracts metadata (filename, type, description) from each section
- Identifies and filters out non-accessible documents (binary files, noise)
- Constructs SEC URLs for each document
- Extracts issuer information when available
- Creates `FilingDocumentMetadata` objects for downstream processing

```python
# Example output format
[
    FilingDocumentMetadata(
        cik="0000123456",
        accession_number="0000123456-25-000123",
        form_type="8-K",
        filename="8-k.htm",
        source_url="https://www.sec.gov/Archives/edgar/data/123456/000012345625000123/8-k.htm",
        is_primary=True,
        is_exhibit=False,
        # ...other metadata
    ),
    FilingDocumentMetadata(
        # Exhibit document metadata
        filename="ex99-1.htm",
        is_primary=False,
        is_exhibit=True,
        # ...
    )
]
```

### Form-Specific SGML Indexing

Form-specific indexers extend the base functionality to:

- Extract form-specific entities from SGML headers (issuers, owners, etc.)
- Locate and isolate embedded XML content within the SGML
- Create structured representations of SGML header information
- Identify entity relationships from SGML header sections
- Prepare embedded content for downstream processing by specialized parsers

For more details on form-specific indexers, see the [forms/README.md](forms/README.md) file.

## Document Processing Flow

The complete document processing flow shows the distinction between indexers and parsers:

```
SgmlTextDocument (.txt file from EDGAR)
       │
       ▼
┌──────────────────┐     ┌────────────────────────┐
│SgmlDocumentIndexer│────►│FilingDocumentMetadata  │
└──────┬───────────┘     │(Document Pointers)      │
       │                 └────────────┬────────────┘
       │                              │
       │                              ▼
       │                  ┌────────────────────────┐
       │                  │FilingDocumentRecord    │
       │                  │(Database-Ready Format) │
       │                  └────────────┬───────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐     ┌────────────────────────┐
│Form-Specific     │     │Database Tables         │
│SGML Indexer      │     │(filing_documents)      │
└──────┬───────────┘     └────────────────────────┘
       │
       ├─── SGML Header Extraction
       │    (entities, relationships)
       │
       └─── Embedded Content Isolation
            (XML, HTML extraction)
            │
            ▼
┌────────────────────────┐
│Form-Specific Parsers   │ <- This is where actual parsing happens
│(XML, HTML processing)  │    (forms/form4_parser.py, etc.)
└────────────────────────┘
```

## Extending the Indexer System

To add support for a new form type:

1. Create a new form-specific indexer extending `SgmlDocumentIndexer`
2. Implement form-specific extraction methods
3. Register the new indexer with `SgmlIndexerFactory`

```python
from parsers.sgml.indexers.sgml_document_indexer import SgmlDocumentIndexer

class Form8KSgmlIndexer(SgmlDocumentIndexer):
    def __init__(self, cik: str, accession_number: str):
        super().__init__(cik, accession_number, "8-K")
        
    # Override or extend methods as needed...

# Register with factory
from parsers.sgml.indexers.sgml_indexer_factory import SgmlIndexerFactory
SgmlIndexerFactory.register_indexer("8-K", Form8KSgmlIndexer)
```

## Related Components

- `SgmlDocumentIndexer` – Main logic for indexing SGML files
- `SgmlIndexerFactory` – Factory for creating appropriate indexers
- `Form4SgmlIndexer` - Specialized indexer for Form 4 filings
- `FilingDocumentMetadata` – Output metadata pointer class (models/dataclasses/filing_document_metadata.py)
- `FilingDocumentRecord` – Adapter destination for database (models/dataclasses/filing_document_record.py)
- `Form4Parser` – *Parser* (not indexer) for Form 4 XML content (parsers/forms/form4_parser.py)
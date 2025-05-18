# models/dataclasses

This module defines the core dataclass models used across the Edgar App platform. These classes serve as transportable, lightweight data models that flow between stages of each pipeline.

## Naming Conventions

Each dataclass adheres to a standardized naming system based on its role in the pipeline:

| Category                   | Suffix/Pattern              | Description                                                                 | Example                         |
|----------------------------|----------------------------|-----------------------------------------------------------------------------|--------------------------------|
| **Data Container**         | `*Document`                | Full transport units, often containing raw or cleaned content              | `RawDocument`, `SgmlTextDocument` |
| **Pointer/Metadata**       | `*Metadata`, `*Record`     | Lightweight identifiers, filenames, URLs, or basic structured metadata     | `FilingMetadata`, `FilingDocumentRecord` |
| **Entity Data**            | `*Data`                    | Specific entity information, often with relationships to other entities     | `EntityData`, `Form4FilingData` |
| **Form-Specific Classes**  | `Form*`                    | Specialized dataclasses for specific SEC form types                        | `Form4FilingData`, `Form4TransactionData` |

## Core Dataclasses

### Base Metadata Classes

- **FilingMetadata** (`filing_metadata.py`)  
  Basic metadata about a filing (accession number, CIK, form type, dates)

- **FilingDocumentMetadata** (`filing_document_metadata.py`)  
  Pointer to a document within a filing, used during parsing phase

- **FilingDocumentRecord** (`filing_document_record.py`)  
  ORM-ready format of document metadata, ready for database storage

### Data Container Classes

- **RawDocument** (`raw_document.py`)  
  Complete filing document with content and metadata

- **SgmlTextDocument** (`sgml_text_document.py`)  
  Specialized container for raw SGML text content and basic metadata

### Entity and Relationship Classes

- **EntityData** (`entity.py`)  
  Represents companies, persons, or other entities in SEC filings

### Form-Specific Classes

Located in the `forms/` subdirectory:

- **Form4FilingData** (`forms/form4_filing.py`)  
  Container for Form 4 filing data, including relationships and transactions

- **Form4RelationshipData** (`forms/form4_relationship.py`)  
  Represents relationships between issuers and reporting owners in Form 4 filings

- **Form4TransactionData** (`forms/form4_transaction.py`)  
  Individual transactions reported in Form 4 filings

## Data Flow

```
FilingMetadata ──────────┐
                         ▼
RawDocument ───────► Processing ───► FilingDocumentMetadata
                                          │
SgmlTextDocument ──────────────────┘     │
                                          ▼
                               FilingDocumentRecord ───► Database
```

## Form-Specific Processing

Form 4 example:
```
RawDocument ───► Form4Parser ───► Form4FilingData
                                     │
                                     ├─► Form4RelationshipData
                                     │
                                     └─► Form4TransactionData
```

## Best Practices

- Dataclasses should only contain primitive types (`str`, `int`, `date`, etc.) or other dataclasses—not ORM instances
- Use `UUID` or `accession_number` consistently for linking between stages
- Include helpful `__repr__` methods to aid in debugging
- Document each class's purpose and position in the data flow
- Add validation in `__post_init__` methods for complex fields
- For form-specific models, include helper properties and methods for common use cases
- Keep relationships between related dataclasses explicit through IDs rather than nested objects
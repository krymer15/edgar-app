# Form-Specific SGML Indexing and Database Design

> **Note:** This document describes how SGML-indexed data is stored in the database schema, with Form 4 as the reference implementation. It focuses on how SGML indexers integrate with the broader database architecture.

## SGML Indexing and Database Integration

The database schema supports specialized SGML indexing by following a normalized design that separates general filing metadata (extracted by all SGML indexers) from form-specific data (extracted by form-specific SGML indexers):

### Core Tables

1. **filing_metadata** ([sql/create/crawler_idx/filing_metadata.sql](../../../../sql/create/crawler_idx/filing_metadata.sql))
   - Primary table for all filings regardless of form type
   - Contains the `accession_number` primary key that links to form-specific tables

2. **filing_documents** ([sql/create/crawler_idx/filing_documents.sql](../../../../sql/create/crawler_idx/filing_documents.sql))
   - Universal document pointer table
   - Tracks all document locations and metadata
   - Includes `issuer_cik` field for direct issuer references

### Form-Specific Tables

3. **entities** ([sql/create/forms/entities.sql](../../../../sql/create/forms/entities.sql))
   - Universal entity registry for companies and individuals
   - Referenced by form-specific relationship tables
   - Supports entity deduplication and tracking

4. **form4_filings** ([sql/create/forms/form4_filings.sql](../../../../sql/create/forms/form4_filings.sql))
   - Top-level table for Form 4 filings
   - Links to `filing_metadata` via `accession_number`
   - Contains only Form 4-specific metadata

5. **form4_relationships** ([sql/create/forms/form4_relationships.sql](../../../../sql/create/forms/form4_relationships.sql))
   - Maps the many-to-many relationships between issuers and reporting owners
   - Tracks relationship types (director, officer, 10% owner, etc.)
   - Links to both entities and form4_filings tables

6. **form4_transactions** ([sql/create/forms/form4_transactions.sql](../../../../sql/create/forms/form4_transactions.sql))
   - Stores detailed transaction data from Form 4 filings
   - Links to both form4_filings and form4_relationships
   - Handles both derivative and non-derivative transactions

## SGML Indexing Architecture

The SGML indexing process is central to the database design:

1. **SGML Indexers**: Extract metadata from SGML structure
   - [`SgmlDocumentIndexer`](../sgml_document_indexer.py): Base indexer for common SGML extraction
   - [`Form4SgmlIndexer`](form4_sgml_indexer.py): Form 4-specific SGML header extraction
   - These extract data from both the SGML header and identify embedded XML sections

2. **XML Processing** (after SGML indexing):
   - XML is isolated by the SGML indexer from within the SGML document
   - [`Form4Parser`](../../../forms/form4_parser.py): Processes the extracted XML content

3. **Database Writers**:
   - [`Form4Writer`](../../../../writers/forms/form4_writer.py): Writes SGML-indexed data to form-specific tables
   - Ensures all metadata extracted from SGML headers is properly stored

## Benefits of This Approach

1. **Proper Entity Modeling**
   - Handles the 1:N relationship between issuers and reporting owners
   - Supports complex relationship types with detailed attributes
   - Enables easy querying of ownership relationships

2. **Separation of Concerns**
   - General filing metadata separated from form-specific data
   - Allows specialized queries on form-specific attributes
   - Avoids bloating the universal filing tables with form-specific fields

3. **Progressive Enhancement**
   - Starts with basic metadata for all filings
   - Adds detailed form-specific data for supported form types
   - Enables form-specific analytics and reporting

4. **Extensibility**
   - Pattern can be extended to other form types (Form 3, Form 5, 8-K, etc.)
   - New form-specific tables can be added without changing core tables
   - Common entity registry facilitates cross-form analysis

## Form-Specific Database Structure

```
filing_metadata (1) ◄──┐
                       │
                       │
                      1:1
                       │
                       │
                       ▼
                  form4_filings
                       │
                       │
                      1:N
                       │
                       ▼
entities ◄────► form4_relationships ◄───── form4_transactions
   ▲          (issuer/owner)
   │                
```

## Implementation in ORM Models

This schema design is implemented in the following ORM model classes:

- [`FilingMetadata`](../../../../models/orm_models/filing_metadata.py): Core filing metadata
- [`FilingDocumentORM`](../../../../models/orm_models/filing_document_orm.py): Document registry
- [`Entity`](../../../../models/orm_models/entity_orm.py): Entity registry
- [`Form4Filing`](../../../../models/orm_models/forms/form4_filing_orm.py): Form 4 specific metadata
- [`Form4Relationship`](../../../../models/orm_models/forms/form4_relationship_orm.py): Issuer-owner relationships
- [`Form4Transaction`](../../../../models/orm_models/forms/form4_transaction_orm.py): Transaction details

## Extending to Other Form Types

This pattern can be extended to other form types following these steps:

1. **Create Form-Specific Tables**
   - Define tables with appropriate relationships to core tables
   - Include only form-specific fields, avoiding duplication

2. **Implement Form-Specific Indexers**
   - Extend the base `SgmlDocumentIndexer` for the form type
   - Extract relevant entities and form-specific data

3. **Define Form-Specific Dataclasses**
   - Create dataclasses for in-memory representation
   - Implement appropriate validation and relationships

4. **Create Form-Specific Writers**
   - Implement database writers for the new tables
   - Include entity resolution and relationship management

## SGML Processing Flow

The SGML indexing and processing flow follows this pattern:

```
SgmlTextDocument (.txt file)
        │
        ▼
┌────────────────────────┐
│ SgmlDocumentIndexer    │ → FilingDocumentMetadata
│ (base extraction)      │   (universal document pointers)
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Form4SgmlIndexer       │ → Form4FilingData
│ (SGML header parsing)  │   (entities, relationships)
└──────────┬─────────────┘
           │
           ├─── Extract XML content from SGML
           │
           ▼
┌────────────────────────┐
│ Form4Parser            │
│ (XML content parsing)  │ → Transaction Data 
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Form4Writer            │
│ (database storage)     │
└──────────┬─────────────┘
           │
           ▼
    Database Tables
```

This flow demonstrates how SGML indexing fits into the broader processing pipeline, with the SGML indexer providing critical extraction services for both document metadata and embedded XML content.

## Design Benefits

This architectural approach ensures:

- Clean separation of general document handling and form-specific processing
- Optimized database schema for each form type
- Efficient queries across different entity types
- Unified document registry with specialized form data
- Progressive enhancement of filing data based on form type

The implemented design successfully balances normalization principles with practical considerations for working with the diverse SEC form types.
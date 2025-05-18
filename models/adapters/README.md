# models/adapters

This module provides conversion utilities to transform between dataclass models and SQLAlchemy ORM models. It serves as a bridge between the in-memory data structures and database persistence layer.

## Current Implementation

### dataclass_to_orm.py

This file contains functions to convert from dataclass instances to ORM models:

- **`convert_to_orm(dataclass_obj: FilingMetadataDC) -> FilingMetadataORM`**  
  Converts a `FilingMetadata` dataclass to a `FilingMetadata` ORM model.

- **`convert_parsed_doc_to_filing_doc(parsed: FilingDocumentMetadata) -> FilingDocDC`**  
  Converts a `FilingDocumentMetadata` dataclass (parser output) to a `FilingDocumentRecord` dataclass (DB-ready format).

- **`convert_filing_doc_to_orm(dc: FilingDocDC) -> FilingDocumentORM`**  
  Converts a `FilingDocumentRecord` dataclass to a `FilingDocumentORM` model for database storage.

## Data Flow with Adapters

```
                  ┌────────────────┐
                  │  Dataclasses   │
                  └────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────┐
│               Adapters                     │
│                                           │
│  FilingMetadataDC ──► FilingMetadataORM   │
│                                           │
│  FilingDocumentMetadata ──► FilingDocDC   │
│                                           │
│  FilingDocDC ──► FilingDocumentORM        │
└───────────────────────────────────────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │   ORM Models   │
                  └────────────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │    Database    │
                  └────────────────┘
```

## Future Extensions

The adapter pattern can be extended to support new forms and data models:

### Form-Specific Adapters (Not Yet Implemented)

Potential future additions:
- `convert_form4_filing_to_orm(form4_data: Form4FilingData) -> Form4Filing`
- `convert_form4_relationship_to_orm(relationship: Form4RelationshipData) -> Form4Relationship`
- `convert_form4_transaction_to_orm(transaction: Form4TransactionData) -> Form4Transaction`
- `convert_entity_to_orm(entity: EntityData) -> Entity`

### ORM to Dataclass (Not Yet Implemented)

Functions to convert from ORM models back to dataclasses could be added in an `orm_to_dataclass.py` file:
- `convert_from_orm(orm_obj: FilingMetadataORM) -> FilingMetadataDC`
- `convert_filing_doc_from_orm(orm: FilingDocumentORM) -> FilingDocDC`

## Benefits of the Adapter Pattern

- **Separation of Concerns**: Keeps dataclasses focused on business logic without ORM dependencies
- **Testability**: Makes dataclass models easier to test without database connections
- **Flexibility**: Allows changing database schema without affecting business logic
- **Type Safety**: Provides explicit conversion between model types
- **Explicit Dependencies**: Makes data flow more obvious across application layers

## Usage Example

```python
# In a writer module
from models.adapters.dataclass_to_orm import convert_to_orm, convert_filing_doc_to_orm

def save_filing_metadata(session, filing_metadata_dc):
    # Convert dataclass to ORM model
    filing_metadata_orm = convert_to_orm(filing_metadata_dc)
    
    # Save to database
    session.add(filing_metadata_orm)
    session.commit()
```
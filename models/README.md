# models/

This directory contains all data definitions for the EDGAR App project, implementing a clear separation between in-memory data structures and database persistence.

## Directory Structure

- **base.py**  
  Defines the SQLAlchemy declarative base used by all ORM models.

- **database.py**  
  Database connection configuration and session management.

- **dataclasses/**  
  Pure `@dataclass` objects used for in-memory data manipulation.
  
- **orm_models/**  
  SQLAlchemy ORM models mapping to the database schema.
  
- **adapters/**  
  Conversion utilities between dataclasses and ORM models.
  
- **schemas/**  
  Reserved for future API schema definitions (e.g., Pydantic models).

## Core Models

### Crawler IDX Pipeline Models

- **FilingMetadata** (orm_models/filing_metadata.py)  
  Maps to `filing_metadata` table, storing core filing information.

- **FilingDocumentORM** (orm_models/filing_document_orm.py)  
  Maps to `filing_documents` table, tracking individual documents within filings.

### Form-Specific Models

- **Form4Filing** (orm_models/forms/form4_filing_orm.py)  
  Maps to `form4_filings` table, containing Form 4 filing data.

- **Form4Relationship** (orm_models/forms/form4_relationship_orm.py)  
  Maps to `form4_relationships` table, representing issuer-owner relationships.

- **Form4Transaction** (orm_models/forms/form4_transaction_orm.py)  
  Maps to `form4_transactions` table, containing individual transactions.

- **Entity** (orm_models/entity_orm.py)  
  Maps to `entities` table, representing companies, persons, and other entities.

### Submissions API Pipeline Models

- **CompaniesMetadata** (companies.py)  
  Maps to `companies_metadata` table, storing company information from the SEC Submissions API.

- **SubmissionsMetadata** (submissions.py)  
  Maps to `submissions_metadata` table, storing filing metadata from the SEC Submissions API.

## Data Flow Architecture

Edgar App implements a layered architecture for data handling:

```
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   Data Sources    │    │   In-Memory Data  │    │  Persistence Layer│
├───────────────────┤    ├───────────────────┤    ├───────────────────┤
│                   │    │                   │    │                   │
│  - SEC API        │    │  - Dataclasses    │    │  - ORM Models     │
│  - EDGAR Website  │--->│  - Raw Documents  │--->│  - Database       │
│  - IDX Files      │    │  - Parsed Results │    │  - SQL Tables     │
│                   │    │                   │    │                   │
└───────────────────┘    └───────────────────┘    └───────────────────┘
                                  ▲                        │
                                  │                        │
                                  └────────────────────────┘
                                   Query/Load via Adapters
```

### Example Data Flow: Filing Documents

```
1. Raw SGML content (.txt file)
   ↓
2. SgmlDocumentIndexer parses → [FilingDocumentMetadata]
   ↓
3. convert_parsed_doc_to_filing_doc() adapter → FilingDocumentRecord
   ↓
4. convert_filing_doc_to_orm() adapter → FilingDocumentORM
   ↓
5. Database (filing_documents table)
```

### Example Data Flow: Form 4

```
1. Raw Form 4 XML content
   ↓
2. Form4Parser parses → Form4FilingData, Form4RelationshipData, Form4TransactionData
   ↓
3. Adapter functions (to be implemented) → ORM models
   ↓
4. Database (form4_filings, form4_relationships, form4_transactions tables)
```

## Schemas Directory (Future Use)

The `schemas/` directory is reserved for future API-facing schema definitions, likely using Pydantic models. Potential use cases include:

- Input validation for public APIs
- Response serialization formats
- OpenAPI/Swagger documentation
- JSON schema definitions

## Design Philosophy

This module architecture follows these design principles:

1. **Clean Separation of Concerns**
   - Dataclasses for business logic
   - ORM models for database persistence 
   - Adapters for conversion between the two

2. **Type Safety and Documentation**
   - All models explicitly define their fields and types
   - Relationships between models are clearly documented

3. **Database Normalization**
   - Foreign keys connect related tables
   - Minimal data duplication
   - Consistent primary key strategy

4. **Testability**
   - In-memory dataclasses can be tested without database dependencies
   - ORM models can be validated independently

5. **Explicit Conversions**
   - No implicit conversions between layers
   - All transformations happen through adapter functions
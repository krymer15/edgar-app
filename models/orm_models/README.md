# models/orm_models

This module contains SQLAlchemy ORM classes that define the database schema for the Edgar App. These classes map Python objects to database tables and provide relationship definitions between them.

## Core ORM Models

- **FilingMetadata** (`filing_metadata.py`)  
  Stores basic filing information with primary key `accession_number`.
  ```python
  # Core fields
  accession_number = Column(Text, primary_key=True)
  cik = Column(Text, nullable=False, index=True)
  form_type = Column(Text, nullable=False)
  filing_date = Column(Date, nullable=False)
  filing_url = Column(Text, nullable=True)
  ```
  References: `sql/create/crawler_idx/filing_metadata.sql`

- **FilingDocumentORM** (`filing_document_orm.py`)  
  Tracks individual documents within filings, including metadata and flags.
  ```python
  # Key fields
  id = Column(UUID(as_uuid=True), primary_key=True)
  accession_number = Column(Text, ForeignKey("filing_metadata.accession_number"))
  cik = Column(Text, nullable=False)
  document_type = Column(Text, nullable=True)
  filename = Column(Text, nullable=True)
  ```
  References: `sql/create/crawler_idx/filing_documents.sql`

- **Entity** (`entity_orm.py`)  
  Represents companies, persons, and other entities in SEC filings.
  ```python
  # Core fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  cik = Column(String, nullable=False, unique=True, index=True)
  name = Column(String, nullable=False)
  entity_type = Column(String, nullable=False)  # 'company', 'person', 'trust', 'group'
  ```
  References: `sql/create/forms/entities.sql`

## Form-Specific ORM Models

Located in the `forms/` subdirectory:

- **Form4Filing** (`forms/form4_filing_orm.py`)  
  Top-level container for Form 4 filings data.
  ```python
  # Core fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  accession_number = Column(String, ForeignKey("filing_metadata.accession_number"))
  period_of_report = Column(Date)
  has_multiple_owners = Column(Boolean, default=False)
  ```
  References: `sql/create/forms/form4_filings.sql`

- **Form4Relationship** (`forms/form4_relationship_orm.py`)  
  Represents the relationship between an issuer and reporting owner in Form 4 filings.
  ```python
  # Key relationships
  form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id"))
  issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
  owner_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
  ```
  References: `sql/create/forms/form4_relationships.sql`

- **Form4Transaction** (`forms/form4_transaction_orm.py`)  
  Individual transactions reported in Form 4 filings.
  ```python
  # Key fields
  form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id"))
  relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id"))
  transaction_code = Column(String, nullable=False)
  transaction_date = Column(Date, nullable=False)
  security_title = Column(String, nullable=False)
  ```
  References: `sql/create/forms/form4_transactions.sql`

## Entity Relationships

### Form 4 Filing Relationships
```
FilingMetadata ◄───────┐
     ▲                 │
     │                 │
     │ 1:1            1:1
     │                 │
     │                 ▼
Entity ◄───────► Form4Relationship ◄───────┐
   ▲           (issuer/owner)              │
   │                  ▲                    │
   │                  │                    │
   │                  │                   1:N
   │                 1:N                   │
   │                  │                    │
   └───────────────── Form4Filing          │
                          ▲                │
                          │                │
                         1:N               │
                          │                │
                          └────── Form4Transaction
```

## SQLAlchemy Features Used

- **Foreign Keys**: Define relationships between tables (e.g., `ForeignKey("filing_metadata.accession_number")`)
- **Indexes**: Optimize query performance (e.g., `Index('idx_form4_relationships_filing_id', 'form4_filing_id')`)
- **Constraints**: Ensure data integrity (e.g., `CheckConstraint("entity_type IN ('company', 'person', 'trust', 'group')")`)
- **Relationships**: Define bidirectional connections between models (e.g., `relationship("FilingMetadata", back_populates="form4_filing")`)
- **Cascades**: Automatically handle related records (e.g., `cascade="all, delete-orphan"`)

## Best Practices

- Add `__repr__` methods to all ORM models to aid debugging
- Include class methods for common query patterns (e.g., `get_by_accession()`)
- Use helper properties for derived values (e.g., `is_purchase`)
- Add validation through database constraints
- Include foreign key constraints with appropriate cascade behavior
- Create indexes on frequently queried columns
- Keep ORM model fields in sync with corresponding database migrations
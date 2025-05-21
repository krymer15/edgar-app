# Form-Specific ORM Models

This directory contains SQLAlchemy ORM models for SEC form-specific data tables, with a focus on Form 4 filings and their associated relationships.

## Form 4 Entity Relationship Model

The Form 4 entity relationship model implements a comprehensive and flexible design for tracking insider trading activities. The model consists of several interconnected components:

### Core Components

1. **Entity Registry** (`entities` table)
   - Universal registry for all entities (companies, persons, trusts, groups)
   - All entities are uniquely identified by CIK
   - Supports multiple entity types via the `entity_type` field
   - Enables cross-referencing between issuers and reporting owners

2. **Form 4 Relationships** (`form4_relationships` table)
   - Represents the relationship between an issuer and a reporting owner
   - Stores relationship types (director, officer, 10% owner, other)
   - Tracks detailed relationship metadata (titles, positions)
   - Supports group filings via the `is_group_filing` flag
   - JSONB field (`relationship_details`) allows for schema evolution

3. **Form 4 Transactions** (`form4_transactions` table)
   - Linked to specific relationships via `relationship_id`
   - Supports multiple transactions per relationship
   - Tracks both derivative and non-derivative transactions
   - Maintains chronological transaction history

### Relationship Types

The model supports these key relationship types:

- **Director**: Board members, indicated by `is_director` flag
- **Officer**: Executives and officers, indicated by `is_officer` flag with `officer_title`
- **10% Owner**: Substantial shareholders, indicated by `is_ten_percent_owner` flag
- **Other**: Other insiders, indicated by `is_other` flag with `other_text` explanation

### Entity Relationship Diagram

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

## Implementation Details

### Form4Filing ORM (`form4_filing_orm.py`)

Top-level container for Form 4 filings:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
accession_number = Column(String, ForeignKey("filing_metadata.accession_number"))
period_of_report = Column(Date)
has_multiple_owners = Column(Boolean, default=False)
```

### Form4Relationship ORM (`form4_relationship_orm.py`)

Represents the relationship between an issuer and reporting owner:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id"))
issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
owner_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
relationship_type = Column(String, nullable=False)
is_director = Column(Boolean, default=False)
is_officer = Column(Boolean, default=False)
is_ten_percent_owner = Column(Boolean, default=False)
is_other = Column(Boolean, default=False)
officer_title = Column(String)
other_text = Column(String)
relationship_details = Column(JSONB)
is_group_filing = Column(Boolean, default=False)
filing_date = Column(Date, nullable=False)
```

### Form4Transaction ORM (`form4_transaction_orm.py`)

Individual transactions reported in Form 4 filings:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id"))
relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id"))
transaction_code = Column(String, nullable=False)
transaction_date = Column(Date, nullable=False)
security_title = Column(String, nullable=False)
acquisition_disposition_flag = Column(String)  # 'A' for Acquisition, 'D' for Disposition
shares_amount = Column(Numeric)
price_per_share = Column(Numeric)
```

### Entity ORM (`entity_orm.py`)

Universal entity registry with bidirectional relationships:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
cik = Column(String, nullable=False, unique=True, index=True)
name = Column(String, nullable=False)
entity_type = Column(String, nullable=False)  # 'company', 'person', 'trust', 'group'

# Relationships to Form4Relationship
issuer_relationships = relationship("Form4Relationship", 
                                   foreign_keys="Form4Relationship.issuer_entity_id",
                                   back_populates="issuer_entity")
owner_relationships = relationship("Form4Relationship",
                                  foreign_keys="Form4Relationship.owner_entity_id",
                                  back_populates="owner_entity")
```

## Planned Enhancements

1. **Position Tracking**
   - Adding `total_shares_owned` field to Form4Relationship to track ownership positions
   - Supporting historical analysis of ownership changes over time

2. **Transaction Classification**
   - Tracks acquisition/disposition flags ('A'/'D') on transactions
   - Enables clear distinction between buying and selling activities
   - Provides improved reporting capabilities for analyzing insider trading patterns

3. **Performance Optimization**
   - Additional indexes for common query patterns
   - Query optimization for relationship traversal

## Design Advantages

This relationship model offers several key advantages:

1. **Normalized Schema**: Properly normalized to minimize data duplication
2. **Flexible Entity Model**: Universal entity registry with type differentiation
3. **Many-to-Many Support**: Robust handling of complex relationships
4. **Group Filing Support**: Proper tracking of group insider filings
5. **Historical Tracking**: Ability to track relationship changes over time
6. **Efficient Queries**: Optimized for common reporting and analysis queries
7. **Schema Evolution**: JSONB fields allow for extending without schema changes

## Usage Notes

When working with these ORM models, note the following best practices:

1. Use the `Entity.get_or_create()` method to ensure entity uniqueness by CIK
2. Use the `Form4Relationship.find_by_entities()` method to locate existing relationships
3. Set appropriate relationship flags based on parsed Form 4 data
4. Ensure proper transaction linking via relationship_id foreign key
5. Use SQLAlchemy's session patterns for efficient relationship traversal

## Related Components

- [Form4RelationshipData Dataclass](../../dataclasses/forms/form4_relationship.py)
- [Form 4 Parser](../../../parsers/forms/form4_parser.py)
- [Form 4 Orchestrator](../../../orchestrators/forms/form4_orchestrator.py)
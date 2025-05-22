# Form-Specific ORM Models

This directory contains SQLAlchemy ORM models for SEC form-specific data tables, with a focus on Form 4 filings and their associated relationships, securities, and transactions.

## Form 4 Models

### Form 4 Entity Relationship Model

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

## Security and Transaction Normalization Models

As part of the Form 4 schema redesign effort, the following models have been implemented to normalize securities and transaction data:

### Security ORM (`security_orm.py`)

Normalized securities table that stores unique securities across all filings:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
title = Column(String, nullable=False)
issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
security_type = Column(String, nullable=False)  # 'equity', 'option', 'convertible', 'other_derivative'
standard_cusip = Column(String)
```

### DerivativeSecurity ORM (`derivative_security_orm.py`)

Stores derivative security-specific details linked to the main securities table:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id"))
underlying_security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id"))
underlying_security_title = Column(String, nullable=False)
conversion_price = Column(Numeric)
exercise_date = Column(Date)
expiration_date = Column(Date)
```

### NonDerivativeTransaction ORM (`non_derivative_transaction_orm.py`)

Normalized non-derivative transactions table:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id"))
relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id"))
security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id"))
transaction_code = Column(String, nullable=False)
transaction_date = Column(Date, nullable=False)
transaction_form_type = Column(String)
shares_amount = Column(Numeric, nullable=False)
price_per_share = Column(Numeric)
direct_ownership = Column(Boolean, nullable=False, default=True)
ownership_nature_explanation = Column(String)
transaction_timeliness = Column(String)
footnote_ids = Column(ARRAY(String))
acquisition_disposition_flag = Column(String, nullable=False)
is_part_of_group_filing = Column(Boolean, default=False)
```

### DerivativeTransaction ORM (`derivative_transaction_orm.py`)

Normalized derivative transactions table:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id"))
relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id"))
security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id"))
derivative_security_id = Column(UUID(as_uuid=True), ForeignKey("derivative_securities.id"))
transaction_code = Column(String, nullable=False)
transaction_date = Column(Date, nullable=False)
transaction_form_type = Column(String)
derivative_shares_amount = Column(Numeric, nullable=False)
price_per_derivative = Column(Numeric)
underlying_shares_amount = Column(Numeric)
direct_ownership = Column(Boolean, nullable=False, default=True)
ownership_nature_explanation = Column(String)
transaction_timeliness = Column(String)
footnote_ids = Column(ARRAY(String))
acquisition_disposition_flag = Column(String, nullable=False)
is_part_of_group_filing = Column(Boolean, default=False)
```

## Security and Transaction Services

The schema redesign includes service classes that provide functionality for managing securities and transactions:

1. **SecurityService**
   - Creating and retrieving normalized securities
   - Finding securities by title and issuer
   - Managing derivative securities with their specific attributes

2. **TransactionService**
   - Creating and retrieving non-derivative and derivative transactions
   - Finding transactions by various criteria (security, filing, relationship)
   - Supporting date range queries for transaction analysis

## Planned Enhancements

1. **Position Tracking**
   - Adding `relationship_positions` table to track ownership positions
   - Supporting historical analysis of ownership changes over time

2. **Transaction Integration**
   - Updating Form4Parser to utilize the new normalized transaction models
   - Migrating existing data to the new schema

3. **Performance Optimization**
   - Additional indexes for common query patterns
   - Query optimization for relationship traversal

## Design Advantages

This normalized schema offers several key advantages:

1. **Normalized Schema**: Properly normalized to minimize data duplication
2. **Flexible Entity Model**: Universal entity registry with type differentiation
3. **Security Normalization**: Securities are stored once and referenced by multiple transactions
4. **Transaction Separation**: Clear separation between derivative and non-derivative transactions
5. **Historical Tracking**: Ability to track relationship and position changes over time
6. **Efficient Queries**: Optimized for common reporting and analysis queries

## Usage Notes

When working with these ORM models, note the following best practices:

1. Use the `SecurityService.get_or_create_security()` method to ensure security uniqueness
2. Use the `TransactionService` methods for creating and retrieving transactions
3. Link derivative securities to their underlying securities whenever possible
4. Set the appropriate `acquisition_disposition_flag` ('A' or 'D') for all transactions
5. Use the `direct_ownership` flag and `ownership_nature_explanation` to indicate ownership nature
6. Ensure proper transaction linking via relationship_id and security_id foreign keys

## Related Components

- [SecurityData Dataclass](../../dataclasses/forms/security_data.py)
- [DerivativeSecurityData Dataclass](../../dataclasses/forms/derivative_security_data.py)
- [TransactionBase Dataclass](../../dataclasses/forms/transaction_data.py)
- [NonDerivativeTransactionData Dataclass](../../dataclasses/forms/transaction_data.py)
- [DerivativeTransactionData Dataclass](../../dataclasses/forms/transaction_data.py)
- [Security Adapter](../../adapters/security_adapter.py)
- [Transaction Adapter](../../adapters/transaction_adapter.py)
- [Security Service](../../../services/forms/security_service.py)
- [Transaction Service](../../../services/forms/transaction_service.py)
- [Form 4 Parser](../../../parsers/forms/form4_parser.py)
# Form-Related Services

This directory contains service classes that implement business logic related to various SEC forms and their components. Services provide a clean interface for the application to interact with the underlying data models and repositories.

## Security Service

### Overview

The `SecurityService` class (`security_service.py`) provides functionality for managing securities and derivative securities. It is part of the Form 4 schema redesign effort to normalize securities data across filings.

### Key Features

- **Get or Create Securities**: Ensures security uniqueness by title and issuer
- **Securities by Issuer**: Retrieves all securities for a specific issuer
- **Derivative Security Management**: Creates and retrieves derivative securities with their specific attributes
- **Security Lookup**: Finds securities based on various attributes

### Usage Examples

```python
# Initialize service with a database session
security_service = SecurityService(db_session)

# Get or create a security
security_data = SecurityData(
    title="Common Stock",
    issuer_entity_id=issuer_id,
    security_type="equity"
)
security_id = security_service.get_or_create_security(security_data)

# Find a security by attributes
security = security_service.find_security_by_title_and_issuer("Common Stock", issuer_id)

# Get or create a derivative security
derivative_data = DerivativeSecurityData(
    security_id=security_id,
    underlying_security_title="Common Stock",
    conversion_price=Decimal("10.50"),
    exercise_date=date(2023, 5, 15),
    expiration_date=date(2028, 5, 15)
)
derivative_id = security_service.get_or_create_derivative_security(derivative_data)
```

## Transaction Service

### Overview

The `TransactionService` class (`transaction_service.py`) provides functionality for managing non-derivative and derivative transactions. It builds upon the security normalization from Phase 1 and is part of the Form 4 schema redesign effort.

### Key Features

- **Transaction Creation**: Creates and persists transactions of both types
- **Transaction Retrieval**: Fetches transactions by ID or via various filters
- **Filing Integration**: Retrieves all transactions for a specific filing
- **Transaction Queries**: Supports date range and security-specific queries
- **Transaction Updates**: Provides methods for updating and deleting transactions

### Usage Examples

```python
# Initialize service with a database session and security service
transaction_service = TransactionService(db_session, security_service)

# Create a non-derivative transaction
non_derivative_data = NonDerivativeTransactionData(
    relationship_id=relationship_id,
    security_id=security_id,
    transaction_code="P",
    transaction_date=date(2023, 5, 15),
    shares_amount=Decimal("100"),
    acquisition_disposition_flag="A",
    price_per_share=Decimal("10.50"),
    direct_ownership=True
)
transaction_id = transaction_service.create_non_derivative_transaction(non_derivative_data)

# Create a derivative transaction
derivative_data = DerivativeTransactionData(
    relationship_id=relationship_id,
    security_id=security_id,
    derivative_security_id=derivative_security_id,
    transaction_code="A",
    transaction_date=date(2023, 5, 15),
    shares_amount=Decimal("500"),
    acquisition_disposition_flag="A",
    price_per_derivative=Decimal("1.25"),
    underlying_shares_amount=Decimal("500"),
    direct_ownership=False,
    ownership_nature_explanation="By Trust"
)
transaction_id = transaction_service.create_derivative_transaction(derivative_data)

# Get transactions for a filing
non_derivative_txs, derivative_txs = transaction_service.get_transactions_for_filing(filing_id)

# Get transactions for a security in a date range
transactions = transaction_service.get_transactions_for_security(
    security_id, 
    start_date=date(2023, 1, 1), 
    end_date=date(2023, 12, 31)
)
```

## Design Principles

The services in this directory follow these design principles:

1. **Separation of Concerns**: Services handle business logic, separate from data access and presentation
2. **Dependency Injection**: Services receive database sessions and other dependencies rather than creating them
3. **Dataclass-Based Interfaces**: Services accept and return dataclass instances, not ORM models
4. **Adapter Pattern**: Services use adapters to convert between dataclasses and ORM models
5. **Atomic Operations**: Services handle transactions and ensure data consistency

## Position Service

### Overview

The `PositionService` class (`position_service.py`) provides functionality for tracking security positions over time. It is part of Phase 3 of the Form 4 schema redesign effort and builds upon the normalized securities and transactions from earlier phases.

### Key Features

- **Position Creation**: Create position entries from transactions or position-only holdings
- **Position Retrieval**: Fetch positions by ID, relationship, or security with date filtering
- **Position Updates**: Update positions based on transaction impacts with cumulative tracking
- **Position History**: Track complete position change history over time
- **Position Calculations**: Calculate total shares owned per security for relationships
- **Position Recalculation**: Recalculate positions from transaction history when needed

### Usage Examples

```python
# Initialize service with a database session and optional transaction service
position_service = PositionService(db_session, transaction_service)

# Create a position from transaction data
position_data = RelationshipPositionData(
    relationship_id=relationship_id,
    security_id=security_id,
    position_date=date(2023, 5, 15),
    shares_amount=Decimal("1000"),
    filing_id=filing_id,
    position_type="equity",
    direct_ownership=True
)
position_id = position_service.create_position(position_data)

# Update position from a transaction
transaction_data = NonDerivativeTransactionData(...)
new_position_id = position_service.update_position_from_transaction(transaction_data)

# Get latest position for a relationship-security combination
latest_position = position_service.get_latest_position(
    relationship_id=relationship_id,
    security_id=security_id,
    as_of_date=date(2023, 5, 20)
)

# Get all positions for a relationship
positions = position_service.get_positions_for_relationship(relationship_id)

# Calculate total shares owned per security
totals = position_service.calculate_total_shares_owned(relationship_id)

# Get position history with date filtering
history = position_service.get_position_history(
    relationship_id, security_id,
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31)
)

# Create position-only entry (holding without transaction)
position_only = RelationshipPositionData(...)
position_service.create_position_only_entry(position_only)
```

### Position Types

The position service supports two types of positions:

1. **Equity Positions**: Direct holdings of securities
2. **Derivative Positions**: Holdings of derivative securities (options, warrants, etc.)

### Position Calculation Logic

- **Acquisitions**: Add to existing position amounts
- **Dispositions**: Subtract from existing position amounts  
- **Position-Only Entries**: Direct position amounts without transaction impact
- **Cumulative Tracking**: Maintains running totals over time
- **Historical Accuracy**: Preserves complete audit trail of position changes

## Planned Enhancements

As part of the ongoing Form 4 schema redesign, the following enhancements are planned:

1. **Phase 4 - Parser Integration**: Updating the parser to use the normalized security, transaction, and position services
2. **Reporting Service**: For generating analysis and reports on insider trading activities
3. **Incremental Data Migration**: Moving from the legacy form4_transactions table to the new schema
4. **Performance Optimization**: Optimizing position calculations for large datasets

## Related Components

### Data Models
- [Security Data Models](../../models/dataclasses/forms/security_data.py)
- [Derivative Security Data Models](../../models/dataclasses/forms/derivative_security_data.py)
- [Transaction Data Models](../../models/dataclasses/forms/transaction_data.py)
- [Position Data Models](../../models/dataclasses/forms/position_data.py)

### ORM Models
- [Security ORM Models](../../models/orm_models/forms/security_orm.py)
- [Derivative Security ORM Models](../../models/orm_models/forms/derivative_security_orm.py)
- [Non-Derivative Transaction ORM Models](../../models/orm_models/forms/non_derivative_transaction_orm.py)
- [Derivative Transaction ORM Models](../../models/orm_models/forms/derivative_transaction_orm.py)
- [Relationship Position ORM Models](../../models/orm_models/forms/relationship_position_orm.py)

### Adapters
- [Security Adapters](../../models/adapters/security_adapter.py)
- [Transaction Adapters](../../models/adapters/transaction_adapter.py)
- [Position Adapters](../../models/adapters/position_adapter.py)

### Database Schema
- [Relationship Positions Table](../../sql/create/forms/relationship_positions.sql)

### Tests
- [Position Service Tests](../../tests/forms/position/)
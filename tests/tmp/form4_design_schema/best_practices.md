# Form 4 Schema Best Practices

Based on project guidelines in `CLAUDE.md`, this document outlines the best practices implemented in the Form 4 schema redesign.

## Use of @dataclass Containers

Following the guideline to "Use `@dataclass` containers whenever possible to pass raw files or strings between modules", we've implemented a comprehensive set of dataclass models for the Form 4 schema:

1. **Core Data Models**
   - `SecurityData`: For security information
   - `DerivativeSecurityData`: For derivative-specific details
   - `PositionData`: For position information
   - `NonDerivativeTransactionData`: For non-derivative transactions
   - `DerivativeTransactionData`: For derivative transactions

2. **Request/Response Models**
   - `PositionSnapshotRequest`: For position snapshot requests
   - `PositionTimeSeriesRequest`: For position history requests
   - `PositionCalculationRequest`: For recalculation requests
   - `InsiderOwnershipRequest`: For ownership data requests
   - `PositionResult`: For encapsulating API responses

### Benefits of Dataclass Approach

1. **Type Safety**
   - Clear definition of required vs. optional fields
   - Validation in `__post_init__` methods
   - IDE auto-completion support

2. **Data Validation**
   - Built-in validation for security types
   - Validation for acquisition/disposition flags
   - Automatic UUID generation

3. **Improved Code Readability**
   - Clear structure for data passing between components
   - Self-documenting field names
   - Explicit typing

4. **Business Logic Encapsulation**
   - Property methods for calculated values
   - Centralized validation logic
   - Default value handling

## Separation of Concerns

The redesigned schema follows proper separation of concerns:

1. **Data Layer Separation**
   - ORM models for database interaction
   - Dataclass models for business logic and data transfer

2. **Service Layer Architecture**
   - Services responsible for business logic
   - Controllers handle GUI/presentation logic
   - Internal methods handle ORM interactions

3. **Clean Interface Design**
   - Public methods accept and return dataclasses
   - Private methods work with ORM objects internally

## Code Structure Best Practices

1. **Method Naming Conventions**
   - Public methods describe business operations
   - Private methods prefixed with underscore
   - Clear verb-noun structure (e.g., `get_position_history`)

2. **Error Handling**
   - Consistent use of `PositionResult` to encapsulate success/failure
   - Detailed error messages
   - Try-except blocks to prevent cascading failures

3. **Docstrings**
   - All classes and methods have descriptive docstrings
   - Parameter and return type documentation
   - Usage examples where helpful

## Database Best Practices

1. **SQLAlchemy Model Design**
   - Consistent naming conventions
   - Proper relationship definitions
   - Index definitions for performance
   - Check constraints for data integrity

2. **Transaction Management**
   - Explicit transaction control
   - Atomic operations
   - Appropriate use of flush vs. commit

## Implementation Examples

### Dataclass Usage Example

```python
from models.dataclasses.forms.form4_schema import NonDerivativeTransactionData, PositionData

# Creating a transaction dataclass instance
transaction = NonDerivativeTransactionData(
    relationship_id="123e4567-e89b-12d3-a456-426614174000",
    security_id="123e4567-e89b-12d3-a456-426614174001",
    transaction_code="P",
    transaction_date=date(2023, 7, 15),
    shares_amount=Decimal("100.0"),
    acquisition_disposition_flag="A",
    price_per_share=Decimal("25.50")
)

# Position impact is calculated via property
impact = transaction.position_impact  # Returns Decimal("100.0")

# Creating a position from transaction
position = PositionData(
    relationship_id=transaction.relationship_id,
    security_id=transaction.security_id,
    position_date=transaction.transaction_date,
    shares_amount=impact,
    direct_ownership=True
)
```

### Service Layer Example

```python
# Controller method using dataclasses
def get_insider_ownership_data(self, issuer_cik: str, as_of_date: Optional[date] = None) -> Dict[str, Any]:
    # Create request dataclass
    request = InsiderOwnershipRequest(issuer_cik=issuer_cik, as_of_date=as_of_date)
    
    # Call service with dataclass
    result = self.position_service.get_insider_ownership(request)
    
    # Handle result dataclass
    if not result.success:
        return {"error": result.error_message}
    
    return result.data
```

### Database Interaction Example

```python
# Proper ORM usage with dataclass conversion
def _orm_to_dataclass(self, position_orm: RelationshipPosition) -> PositionData:
    """Convert ORM position to dataclass"""
    return PositionData(
        id=str(position_orm.id),
        relationship_id=str(position_orm.relationship_id),
        security_id=str(position_orm.security_id),
        position_date=position_orm.position_date,
        shares_amount=position_orm.shares_amount,
        direct_ownership=position_orm.direct_ownership,
        ownership_nature_explanation=position_orm.ownership_nature_explanation,
        filing_id=str(position_orm.filing_id),
        transaction_id=str(position_orm.transaction_id) if position_orm.transaction_id else None
    )
```
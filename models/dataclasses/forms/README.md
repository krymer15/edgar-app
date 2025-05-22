# Form-Related Dataclass Models

This directory contains dataclass models for various SEC forms and their related components. Dataclasses provide a clean interface for transferring data between service layers and are used throughout the application for domain object manipulation.

## Core Form 4 Dataclasses

- `form4_filing.py` - Represents the top-level Form 4 filing data
- `form4_relationship.py` - Represents the relationship between an issuer and reporting owner
- `form4_transaction.py` - Represents transactions reported in Form 4 filings

## Form 4 Schema Redesign Dataclasses

As part of the Form 4 schema redesign effort, the following dataclasses have been implemented:

- `security_data.py` - Represents normalized security data across filings
- `derivative_security_data.py` - Contains derivative security-specific details
- `transaction_data.py` - Provides base class and implementations for both non-derivative and derivative transactions

## Dataclass Features

### SecurityData

The `SecurityData` class provides the following features:

```python
@dataclass
class SecurityData:
    """Dataclass for transferring security information between service layers"""
    title: str
    issuer_entity_id: str
    security_type: str  # 'equity', 'option', 'convertible', 'other_derivative'
    standard_cusip: Optional[str] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        # Generate ID if not provided
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate security type
        valid_types = ['equity', 'option', 'convertible', 'other_derivative']
        if self.security_type not in valid_types:
            raise ValueError(f"Invalid security type: {self.security_type}. Must be one of {valid_types}")
```

### DerivativeSecurityData

The `DerivativeSecurityData` class provides derivative-specific attributes:

```python
@dataclass
class DerivativeSecurityData:
    """Dataclass for derivative security details"""
    security_id: str
    underlying_security_title: str
    conversion_price: Optional[Decimal] = None
    exercise_date: Optional[date] = None
    expiration_date: Optional[date] = None
    underlying_security_id: Optional[str] = None
    id: Optional[str] = None
```

### TransactionBase, NonDerivativeTransactionData, and DerivativeTransactionData

The transaction dataclasses provide a hierarchical model for Form 4 transactions:

```python
@dataclass
class TransactionBase:
    """Base class for transaction data"""
    relationship_id: str
    security_id: str
    transaction_code: str
    transaction_date: date
    shares_amount: Decimal
    acquisition_disposition_flag: str  # 'A' or 'D'
    direct_ownership: bool = True
    ownership_nature_explanation: Optional[str] = None
    transaction_form_type: Optional[str] = None
    transaction_timeliness: Optional[str] = None
    footnote_ids: List[str] = field(default_factory=list)
    form4_filing_id: Optional[str] = None
    id: Optional[str] = None
    is_part_of_group_filing: bool = False
    
    @property
    def position_impact(self) -> Decimal:
        """Calculate the impact on the position (positive for acquisitions, negative for dispositions)"""
        if self.acquisition_disposition_flag == 'A':
            return self.shares_amount
        elif self.acquisition_disposition_flag == 'D':
            return -1 * self.shares_amount
        return Decimal('0')
```

```python
@dataclass
class NonDerivativeTransactionData(TransactionBase):
    """Data for non-derivative transactions"""
    price_per_share: Optional[Decimal] = None
```

```python
@dataclass
class DerivativeTransactionData(TransactionBase):
    """Data for derivative transactions"""
    derivative_security_id: str
    price_per_derivative: Optional[Decimal] = None
    underlying_shares_amount: Optional[Decimal] = None
    
    @property
    def derivative_shares_amount(self) -> Decimal:
        return self.shares_amount
```

## Usage Guidelines

- Use dataclasses for transferring data between service layers and domain logic
- Adapt dataclasses to ORM models using adapter functions in the `models.adapters` module
- Leverage `__post_init__` for validation and type conversion
- Use optional fields with sensible defaults where appropriate
- Follow the project convention of including `id` field that auto-generates UUIDs for new instances

## Related Components

- [Security ORM Models](../../orm_models/forms/security_orm.py)
- [Derivative Security ORM Models](../../orm_models/forms/derivative_security_orm.py)
- [Non-Derivative Transaction ORM Models](../../orm_models/forms/non_derivative_transaction_orm.py)
- [Derivative Transaction ORM Models](../../orm_models/forms/derivative_transaction_orm.py)
- [Security Adapter](../../adapters/security_adapter.py)
- [Transaction Adapter](../../adapters/transaction_adapter.py)
- [Security Service](../../../services/forms/security_service.py)
- [Transaction Service](../../../services/forms/transaction_service.py)
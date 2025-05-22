# Form 4 Transaction Data Models

This document provides detailed information about the transaction data models implemented as part of the Form 4 schema redesign (Phase 2).

## Transaction Schema Design

The transaction schema is designed to normalize transaction data from Form 4 filings, separating non-derivative and derivative transactions into distinct tables while maintaining relationships to securities, filings, and relationships.

### Transaction Data Model Hierarchy

```
                    TransactionBase
                    /            \
                   /              \
NonDerivativeTransactionData    DerivativeTransactionData
```

### Schema Overview

1. **TransactionBase**
   - Common attributes for all transaction types
   - Relationship and security references
   - Transaction metadata

2. **NonDerivativeTransactionData**
   - Equity-specific transaction details
   - Price per share information

3. **DerivativeTransactionData**
   - Derivative-specific transaction details
   - References to derivative securities
   - Underlying shares information

## Database Schema

### Non-Derivative Transactions Table

```sql
CREATE TABLE public.non_derivative_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    form4_filing_id uuid NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    transaction_code text NOT NULL,
    transaction_date date NOT NULL,
    transaction_form_type text NULL,
    shares_amount numeric NOT NULL,
    price_per_share numeric NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    transaction_timeliness text NULL,
    footnote_ids text[] NULL,
    acquisition_disposition_flag text NOT NULL,
    is_part_of_group_filing boolean DEFAULT false NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT non_derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);
```

### Derivative Transactions Table

```sql
CREATE TABLE public.derivative_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    form4_filing_id uuid NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    derivative_security_id uuid NOT NULL,
    transaction_code text NOT NULL,
    transaction_date date NOT NULL,
    transaction_form_type text NULL,
    derivative_shares_amount numeric NOT NULL,
    price_per_derivative numeric NULL,
    underlying_shares_amount numeric NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    transaction_timeliness text NULL,
    footnote_ids text[] NULL,
    acquisition_disposition_flag text NOT NULL,
    is_part_of_group_filing boolean DEFAULT false NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);
```

## Key Fields Explained

### Common Transaction Fields

- **relationship_id**: Links to the form4_relationships table, connecting the transaction to the issuer-owner relationship
- **security_id**: Links to the normalized securities table
- **transaction_code**: SEC transaction code (e.g., 'P' for purchase, 'S' for sale, 'A' for grant)
- **transaction_date**: Date of the transaction
- **shares_amount**: Number of shares/units involved in the transaction
- **acquisition_disposition_flag**: 'A' for acquisition, 'D' for disposition
- **direct_ownership**: Boolean indicating direct ownership (true) or indirect ownership (false)
- **ownership_nature_explanation**: Explanation for indirect ownership (e.g., "By Trust", "By LLC")

### Non-Derivative Transaction Specific Fields

- **price_per_share**: Price per share for the transaction

### Derivative Transaction Specific Fields

- **derivative_security_id**: Links to the derivative_securities table
- **price_per_derivative**: Price per derivative security
- **underlying_shares_amount**: Number of underlying shares represented by the derivative security

## Transaction Codes

The `transaction_code` field contains SEC-defined codes that indicate the nature of the transaction:

- **P**: Open market or private purchase
- **S**: Open market or private sale
- **A**: Grant, award, or other acquisition
- **D**: Disposition to the issuer (e.g., forfeiture)
- **M**: Exercise of derivative security
- **C**: Conversion of derivative security
- **G**: Gift
- **V**: Discretionary transaction
- **J**: Other acquisition or disposition
- **K**: Transaction in equity swap
- **H**: Expiration of short derivative position
- **F**: Exercise of right for in-the-money derivative security
- **E**: Expiration of long derivative position

## Acquisition vs. Disposition

The `acquisition_disposition_flag` field explicitly indicates whether the transaction:

- **A**: Results in an increase in shares owned (Acquisition)
- **D**: Results in a decrease in shares owned (Disposition)

This field simplifies position calculations and reporting.

## Position Impact Calculation

The `position_impact` property calculates the impact of a transaction on the owner's position:

```python
@property
def position_impact(self) -> Decimal:
    """Calculate the impact on the position (positive for acquisitions, negative for dispositions)"""
    if self.acquisition_disposition_flag == 'A':
        return self.shares_amount
    elif self.acquisition_disposition_flag == 'D':
        return -1 * self.shares_amount
    return Decimal('0')
```

## Ownership Nature

Form 4 filings distinguish between:

- **Direct Ownership**: Owner directly holds the securities
- **Indirect Ownership**: Securities held through another entity (trust, LLC, etc.)

The schema captures this using:
- `direct_ownership` boolean flag
- `ownership_nature_explanation` text field for indirect ownership details

## Data Model Implementation

### Transaction Base Class

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
```

### Non-Derivative Transaction Class

```python
@dataclass
class NonDerivativeTransactionData(TransactionBase):
    """Data for non-derivative transactions"""
    price_per_share: Optional[Decimal] = None
```

### Derivative Transaction Class

```python
@dataclass
class DerivativeTransactionData(TransactionBase):
    """Data for derivative transactions"""
    derivative_security_id: str
    price_per_derivative: Optional[Decimal] = None
    underlying_shares_amount: Optional[Decimal] = None
```

## Relationships

The transaction tables maintain relationships to:

- **form4_filings**: The parent filing
- **form4_relationships**: The issuer-owner relationship
- **securities**: The normalized security reference
- **derivative_securities**: The derivative security details (for derivative transactions)

## Usage in Form4Parser

The Form 4 parser will need to be updated to:

1. Extract transaction data from XML
2. Normalize security references using SecurityService
3. Create appropriate transaction records using TransactionService
4. Handle both non-derivative and derivative transactions separately

## Next Steps: Position Tracking

Phase 3 of the Form 4 schema redesign will build on these transaction tables to implement position tracking, which will:

1. Calculate cumulative positions based on transaction history
2. Create a relationship_positions table to track positions over time
3. Support time-series analysis of ownership changes
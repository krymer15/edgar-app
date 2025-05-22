# Phase 2: Transaction Table Migration Implementation (FOR IMPLEMENTATION)

This document outlines the specific implementation details for Phase 2 of the Form 4 schema redesign: Transaction Table Migration. This phase builds on the security normalization from Phase 1 and focuses on creating normalized transaction tables.

## Database Schema

### Core Tables to Create

```sql
-- Non-derivative transactions table
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
    CONSTRAINT non_derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT non_derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_transactions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);

CREATE INDEX idx_non_derivative_transactions_filing ON public.non_derivative_transactions USING btree (form4_filing_id);
CREATE INDEX idx_non_derivative_transactions_relationship ON public.non_derivative_transactions USING btree (relationship_id);
CREATE INDEX idx_non_derivative_transactions_security ON public.non_derivative_transactions USING btree (security_id);
CREATE INDEX idx_non_derivative_transactions_date ON public.non_derivative_transactions USING btree (transaction_date);

-- Derivative transactions table
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
    CONSTRAINT derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_derivative_fkey FOREIGN KEY (derivative_security_id) 
        REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);

CREATE INDEX idx_derivative_transactions_filing ON public.derivative_transactions USING btree (form4_filing_id);
CREATE INDEX idx_derivative_transactions_relationship ON public.derivative_transactions USING btree (relationship_id);
CREATE INDEX idx_derivative_transactions_security ON public.derivative_transactions USING btree (security_id);
CREATE INDEX idx_derivative_transactions_derivative ON public.derivative_transactions USING btree (derivative_security_id);
CREATE INDEX idx_derivative_transactions_date ON public.derivative_transactions USING btree (transaction_date);
```

## SQLAlchemy ORM Models

### Non-Derivative Transaction ORM Model

```python
# models/orm_models/forms/non_derivative_transaction_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base  # Base is from sqlalchemy.orm declarative_base()

class NonDerivativeTransaction(Base):
    __tablename__ = "non_derivative_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_non_derivative_transactions_filing', 'form4_filing_id'),
        Index('idx_non_derivative_transactions_relationship', 'relationship_id'),
        Index('idx_non_derivative_transactions_security', 'security_id'),
        Index('idx_non_derivative_transactions_date', 'transaction_date'),
        CheckConstraint("acquisition_disposition_flag IN ('A', 'D')", name="non_derivative_ad_flag_check"),
    )

    # Relationships
    form4_filing = relationship("Form4Filing", foreign_keys=[form4_filing_id])
    relationship = relationship("Form4Relationship", foreign_keys=[relationship_id])
    security = relationship("Security", foreign_keys=[security_id])

    def __repr__(self):
        return f"<NonDerivativeTransaction(id='{self.id}', code='{self.transaction_code}', date='{self.transaction_date}')>"
```

### Derivative Transaction ORM Model

```python
# models/orm_models/forms/derivative_transaction_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base  # Base is from sqlalchemy.orm declarative_base()

class DerivativeTransaction(Base):
    __tablename__ = "derivative_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    derivative_security_id = Column(UUID(as_uuid=True), ForeignKey("derivative_securities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_derivative_transactions_filing', 'form4_filing_id'),
        Index('idx_derivative_transactions_relationship', 'relationship_id'),
        Index('idx_derivative_transactions_security', 'security_id'),
        Index('idx_derivative_transactions_derivative', 'derivative_security_id'),
        Index('idx_derivative_transactions_date', 'transaction_date'),
        CheckConstraint("acquisition_disposition_flag IN ('A', 'D')", name="derivative_ad_flag_check"),
    )

    # Relationships
    form4_filing = relationship("Form4Filing", foreign_keys=[form4_filing_id])
    relationship = relationship("Form4Relationship", foreign_keys=[relationship_id])
    security = relationship("Security", foreign_keys=[security_id])
    derivative_security = relationship("DerivativeSecurity", foreign_keys=[derivative_security_id])

    def __repr__(self):
        return f"<DerivativeTransaction(id='{self.id}', code='{self.transaction_code}', date='{self.transaction_date}')>"
```

## Dataclass Models

### Transaction Base Dataclass

```python
# models/dataclasses/forms/transaction_data.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from decimal import Decimal
import uuid

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
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate acquisition_disposition_flag
        if self.acquisition_disposition_flag not in ['A', 'D']:
            raise ValueError(f"Invalid acquisition_disposition_flag: {self.acquisition_disposition_flag}. Must be 'A' or 'D'")
    
    @property
    def position_impact(self) -> Decimal:
        """Calculate the impact on the position (positive for acquisitions, negative for dispositions)"""
        if self.acquisition_disposition_flag == 'A':
            return self.shares_amount
        elif self.acquisition_disposition_flag == 'D':
            return -1 * self.shares_amount
        return Decimal('0')


@dataclass
class NonDerivativeTransactionData(TransactionBase):
    """Data for non-derivative transactions"""
    price_per_share: Optional[Decimal] = None


@dataclass
class DerivativeTransactionData(TransactionBase):
    """Data for derivative transactions"""
    derivative_security_id: str
    price_per_derivative: Optional[Decimal] = None
    underlying_shares_amount: Optional[Decimal] = None
    
    # Override shares_amount to rename to derivative_shares_amount for clarity
    @property
    def derivative_shares_amount(self) -> Decimal:
        return self.shares_amount
        
    @derivative_shares_amount.setter
    def derivative_shares_amount(self, value: Decimal):
        self.shares_amount = value
```

## Adapter Implementation

```python
# models/adapters/transaction_adapter.py
import uuid
from typing import List, Optional, Dict

from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from models.orm_models.forms.non_derivative_transaction_orm import NonDerivativeTransaction
from models.orm_models.forms.derivative_transaction_orm import DerivativeTransaction

def convert_non_derivative_transaction_data_to_orm(transaction_data: NonDerivativeTransactionData) -> NonDerivativeTransaction:
    """Convert NonDerivativeTransactionData dataclass to NonDerivativeTransaction ORM model"""
    return NonDerivativeTransaction(
        id=uuid.UUID(transaction_data.id) if transaction_data.id else None,
        form4_filing_id=uuid.UUID(transaction_data.form4_filing_id) if transaction_data.form4_filing_id else None,
        relationship_id=uuid.UUID(transaction_data.relationship_id),
        security_id=uuid.UUID(transaction_data.security_id),
        transaction_code=transaction_data.transaction_code,
        transaction_date=transaction_data.transaction_date,
        transaction_form_type=transaction_data.transaction_form_type,
        shares_amount=transaction_data.shares_amount,
        price_per_share=transaction_data.price_per_share,
        direct_ownership=transaction_data.direct_ownership,
        ownership_nature_explanation=transaction_data.ownership_nature_explanation,
        transaction_timeliness=transaction_data.transaction_timeliness,
        footnote_ids=transaction_data.footnote_ids,
        acquisition_disposition_flag=transaction_data.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_data.is_part_of_group_filing
    )

def convert_non_derivative_transaction_orm_to_data(transaction_orm: NonDerivativeTransaction) -> NonDerivativeTransactionData:
    """Convert NonDerivativeTransaction ORM model to NonDerivativeTransactionData dataclass"""
    return NonDerivativeTransactionData(
        id=str(transaction_orm.id),
        form4_filing_id=str(transaction_orm.form4_filing_id) if transaction_orm.form4_filing_id else None,
        relationship_id=str(transaction_orm.relationship_id),
        security_id=str(transaction_orm.security_id),
        transaction_code=transaction_orm.transaction_code,
        transaction_date=transaction_orm.transaction_date,
        transaction_form_type=transaction_orm.transaction_form_type,
        shares_amount=transaction_orm.shares_amount,
        price_per_share=transaction_orm.price_per_share,
        direct_ownership=transaction_orm.direct_ownership,
        ownership_nature_explanation=transaction_orm.ownership_nature_explanation,
        transaction_timeliness=transaction_orm.transaction_timeliness,
        footnote_ids=transaction_orm.footnote_ids if transaction_orm.footnote_ids else [],
        acquisition_disposition_flag=transaction_orm.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_orm.is_part_of_group_filing
    )

def convert_derivative_transaction_data_to_orm(transaction_data: DerivativeTransactionData) -> DerivativeTransaction:
    """Convert DerivativeTransactionData dataclass to DerivativeTransaction ORM model"""
    return DerivativeTransaction(
        id=uuid.UUID(transaction_data.id) if transaction_data.id else None,
        form4_filing_id=uuid.UUID(transaction_data.form4_filing_id) if transaction_data.form4_filing_id else None,
        relationship_id=uuid.UUID(transaction_data.relationship_id),
        security_id=uuid.UUID(transaction_data.security_id),
        derivative_security_id=uuid.UUID(transaction_data.derivative_security_id),
        transaction_code=transaction_data.transaction_code,
        transaction_date=transaction_data.transaction_date,
        transaction_form_type=transaction_data.transaction_form_type,
        derivative_shares_amount=transaction_data.shares_amount,
        price_per_derivative=transaction_data.price_per_derivative,
        underlying_shares_amount=transaction_data.underlying_shares_amount,
        direct_ownership=transaction_data.direct_ownership,
        ownership_nature_explanation=transaction_data.ownership_nature_explanation,
        transaction_timeliness=transaction_data.transaction_timeliness,
        footnote_ids=transaction_data.footnote_ids,
        acquisition_disposition_flag=transaction_data.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_data.is_part_of_group_filing
    )

def convert_derivative_transaction_orm_to_data(transaction_orm: DerivativeTransaction) -> DerivativeTransactionData:
    """Convert DerivativeTransaction ORM model to DerivativeTransactionData dataclass"""
    return DerivativeTransactionData(
        id=str(transaction_orm.id),
        form4_filing_id=str(transaction_orm.form4_filing_id) if transaction_orm.form4_filing_id else None,
        relationship_id=str(transaction_orm.relationship_id),
        security_id=str(transaction_orm.security_id),
        derivative_security_id=str(transaction_orm.derivative_security_id),
        transaction_code=transaction_orm.transaction_code,
        transaction_date=transaction_orm.transaction_date,
        transaction_form_type=transaction_orm.transaction_form_type,
        shares_amount=transaction_orm.derivative_shares_amount,
        price_per_derivative=transaction_orm.price_per_derivative,
        underlying_shares_amount=transaction_orm.underlying_shares_amount,
        direct_ownership=transaction_orm.direct_ownership,
        ownership_nature_explanation=transaction_orm.ownership_nature_explanation,
        transaction_timeliness=transaction_orm.transaction_timeliness,
        footnote_ids=transaction_orm.footnote_ids if transaction_orm.footnote_ids else [],
        acquisition_disposition_flag=transaction_orm.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_orm.is_part_of_group_filing
    )
```

## Service Implementation

```python
# services/forms/transaction_service.py
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from decimal import Decimal

from models.orm_models.forms.non_derivative_transaction_orm import NonDerivativeTransaction
from models.orm_models.forms.derivative_transaction_orm import DerivativeTransaction
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from models.adapters.transaction_adapter import (
    convert_non_derivative_transaction_data_to_orm,
    convert_non_derivative_transaction_orm_to_data,
    convert_derivative_transaction_data_to_orm,
    convert_derivative_transaction_orm_to_data
)
from services.forms.security_service import SecurityService

class TransactionService:
    """Service for managing Form 4 transactions"""
    
    def __init__(self, db_session: Session, security_service: Optional[SecurityService] = None):
        self.db_session = db_session
        self.security_service = security_service or SecurityService(db_session)
    
    def create_non_derivative_transaction(self, transaction_data: NonDerivativeTransactionData) -> str:
        """Create a new non-derivative transaction"""
        transaction = convert_non_derivative_transaction_data_to_orm(transaction_data)
        self.db_session.add(transaction)
        self.db_session.flush()  # Generate ID without committing
        
        return str(transaction.id)
    
    def create_derivative_transaction(self, transaction_data: DerivativeTransactionData) -> str:
        """Create a new derivative transaction"""
        transaction = convert_derivative_transaction_data_to_orm(transaction_data)
        self.db_session.add(transaction)
        self.db_session.flush()  # Generate ID without committing
        
        return str(transaction.id)
    
    def get_non_derivative_transaction(self, transaction_id: str) -> Optional[NonDerivativeTransactionData]:
        """Get a non-derivative transaction by ID"""
        transaction = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return None
        
        return convert_non_derivative_transaction_orm_to_data(transaction)
    
    def get_derivative_transaction(self, transaction_id: str) -> Optional[DerivativeTransactionData]:
        """Get a derivative transaction by ID"""
        transaction = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return None
        
        return convert_derivative_transaction_orm_to_data(transaction)
    
    def get_transactions_for_filing(self, filing_id: str) -> Tuple[List[NonDerivativeTransactionData], List[DerivativeTransactionData]]:
        """Get all transactions for a specific filing"""
        non_derivative = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.form4_filing_id == filing_id
        ).all()
        
        derivative = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.form4_filing_id == filing_id
        ).all()
        
        return (
            [convert_non_derivative_transaction_orm_to_data(t) for t in non_derivative],
            [convert_derivative_transaction_orm_to_data(t) for t in derivative]
        )
    
    def get_transactions_for_relationship(self, relationship_id: str) -> Tuple[List[NonDerivativeTransactionData], List[DerivativeTransactionData]]:
        """Get all transactions for a specific relationship"""
        non_derivative = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.relationship_id == relationship_id
        ).all()
        
        derivative = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.relationship_id == relationship_id
        ).all()
        
        return (
            [convert_non_derivative_transaction_orm_to_data(t) for t in non_derivative],
            [convert_derivative_transaction_orm_to_data(t) for t in derivative]
        )
    
    def get_transactions_for_security(self, security_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[NonDerivativeTransactionData]:
        """Get all non-derivative transactions for a specific security"""
        query = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.security_id == security_id
        )
        
        if start_date:
            query = query.filter(NonDerivativeTransaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(NonDerivativeTransaction.transaction_date <= end_date)
        
        transactions = query.order_by(NonDerivativeTransaction.transaction_date).all()
        
        return [convert_non_derivative_transaction_orm_to_data(t) for t in transactions]
    
    def get_transactions_for_derivative_security(self, derivative_security_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[DerivativeTransactionData]:
        """Get all derivative transactions for a specific derivative security"""
        query = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.derivative_security_id == derivative_security_id
        )
        
        if start_date:
            query = query.filter(DerivativeTransaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(DerivativeTransaction.transaction_date <= end_date)
        
        transactions = query.order_by(DerivativeTransaction.transaction_date).all()
        
        return [convert_derivative_transaction_orm_to_data(t) for t in transactions]
```

## Migration Script

```sql
-- migration/V21__create_transaction_tables.sql

-- Non-derivative transactions table
CREATE TABLE IF NOT EXISTS public.non_derivative_transactions (
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
    CONSTRAINT non_derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT non_derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_transactions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);

-- Create indexes for non-derivative transactions
CREATE INDEX IF NOT EXISTS idx_non_derivative_transactions_filing ON public.non_derivative_transactions USING btree (form4_filing_id);
CREATE INDEX IF NOT EXISTS idx_non_derivative_transactions_relationship ON public.non_derivative_transactions USING btree (relationship_id);
CREATE INDEX IF NOT EXISTS idx_non_derivative_transactions_security ON public.non_derivative_transactions USING btree (security_id);
CREATE INDEX IF NOT EXISTS idx_non_derivative_transactions_date ON public.non_derivative_transactions USING btree (transaction_date);

-- Derivative transactions table
CREATE TABLE IF NOT EXISTS public.derivative_transactions (
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
    CONSTRAINT derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_derivative_fkey FOREIGN KEY (derivative_security_id) 
        REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);

-- Create indexes for derivative transactions
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_filing ON public.derivative_transactions USING btree (form4_filing_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_relationship ON public.derivative_transactions USING btree (relationship_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_security ON public.derivative_transactions USING btree (security_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_derivative ON public.derivative_transactions USING btree (derivative_security_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_date ON public.derivative_transactions USING btree (transaction_date);
```

## Unit Tests

The unit tests for these transaction models should follow the approach used in Phase 1, using mock-based testing to avoid circular dependencies.

## Next Steps After Phase 2

1. **Integration with Form4Parser**:
   - Update the parser to use the SecurityService to normalized securities
   - Refactor to store transactions using the TransactionService

2. **Position Tracking Planning**:
   - Design the relationship_positions table structure
   - Develop algorithms for position calculation

3. **Documentation**:
   - Update READMEs in relevant folders
   - Document the transaction normalization approach
   - Create documentation for the transaction service
# Phase 3: Position Tracking Implementation (FOR IMPLEMENTATION)

This document outlines the specific implementation details for Phase 3 of the Form 4 schema redesign: Position Tracking. This phase builds on the transaction normalization from Phase 2 and focuses on creating a system to track security positions over time.

## Database Schema

### Core Table to Create

```sql
-- Relationship positions table for tracking current positions
CREATE TABLE public.relationship_positions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    position_date date NOT NULL,
    shares_amount numeric NOT NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    filing_id uuid NOT NULL,
    transaction_id uuid NULL,
    is_position_only boolean DEFAULT false NOT NULL,
    position_type text NOT NULL, -- 'equity' or 'derivative'
    derivative_security_id uuid NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT relationship_positions_pkey PRIMARY KEY (id),
    CONSTRAINT relationship_positions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_filing_fkey FOREIGN KEY (filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_derivative_fkey FOREIGN KEY (derivative_security_id) 
        REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT position_type_check CHECK (position_type IN ('equity', 'derivative'))
);

CREATE INDEX idx_relationship_positions_relationship ON public.relationship_positions USING btree (relationship_id);
CREATE INDEX idx_relationship_positions_security ON public.relationship_positions USING btree (security_id);
CREATE INDEX idx_relationship_positions_date ON public.relationship_positions USING btree (position_date);
CREATE INDEX idx_relationship_positions_derivative ON public.relationship_positions USING btree (derivative_security_id);
CREATE INDEX idx_relationship_positions_filing ON public.relationship_positions USING btree (filing_id);
CREATE UNIQUE INDEX idx_relationship_position_unique ON public.relationship_positions USING btree (relationship_id, security_id, position_date, derivative_security_id, direct_ownership) WHERE (is_position_only = true);
```

## SQLAlchemy ORM Model

### Position ORM Model

```python
# models/orm_models/forms/relationship_position_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base  # Base is from sqlalchemy.orm declarative_base()

class RelationshipPosition(Base):
    __tablename__ = "relationship_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    position_date = Column(Date, nullable=False)
    shares_amount = Column(Numeric, nullable=False)
    direct_ownership = Column(Boolean, nullable=False, default=True)
    ownership_nature_explanation = Column(String)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True))
    is_position_only = Column(Boolean, nullable=False, default=False)
    position_type = Column(String, nullable=False)  # 'equity' or 'derivative'
    derivative_security_id = Column(UUID(as_uuid=True), ForeignKey("derivative_securities.id", ondelete="CASCADE", onupdate="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_relationship_positions_relationship', 'relationship_id'),
        Index('idx_relationship_positions_security', 'security_id'),
        Index('idx_relationship_positions_date', 'position_date'),
        Index('idx_relationship_positions_derivative', 'derivative_security_id'),
        Index('idx_relationship_positions_filing', 'filing_id'),
        Index('idx_relationship_position_unique', 'relationship_id', 'security_id', 'position_date', 'derivative_security_id', 'direct_ownership', unique=True, postgresql_where=(is_position_only == True)),
        CheckConstraint("position_type IN ('equity', 'derivative')", name="position_type_check"),
    )

    # Relationships
    relationship = relationship("Form4Relationship", foreign_keys=[relationship_id])
    security = relationship("Security", foreign_keys=[security_id])
    filing = relationship("Form4Filing", foreign_keys=[filing_id])
    derivative_security = relationship("DerivativeSecurity", foreign_keys=[derivative_security_id])

    def __repr__(self):
        return f"<RelationshipPosition(id='{self.id}', relationship_id='{self.relationship_id}', security_id='{self.security_id}', date='{self.position_date}', shares='{self.shares_amount}')>"
```

## Dataclass Model

### Position Dataclass

```python
# models/dataclasses/forms/position_data.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from decimal import Decimal
import uuid

@dataclass
class RelationshipPositionData:
    """Dataclass for relationship position data"""
    relationship_id: str
    security_id: str
    position_date: date
    shares_amount: Decimal
    filing_id: str
    position_type: str  # 'equity' or 'derivative'
    direct_ownership: bool = True
    ownership_nature_explanation: Optional[str] = None
    transaction_id: Optional[str] = None
    is_position_only: bool = False
    derivative_security_id: Optional[str] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        # Generate ID if not provided
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate position_type
        valid_types = ['equity', 'derivative']
        if self.position_type not in valid_types:
            raise ValueError(f"Invalid position_type: {self.position_type}. Must be one of {valid_types}")
            
        # Ensure derivative_security_id is present for derivative positions
        if self.position_type == 'derivative' and not self.derivative_security_id:
            raise ValueError("derivative_security_id is required for derivative positions")
            
        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.shares_amount, (float, int)):
            self.shares_amount = Decimal(str(self.shares_amount))
```

## Adapter Implementation

```python
# models/adapters/position_adapter.py
import uuid
from typing import List, Optional, Dict

from models.dataclasses.forms.position_data import RelationshipPositionData
from models.orm_models.forms.relationship_position_orm import RelationshipPosition

def convert_position_data_to_orm(position_data: RelationshipPositionData) -> RelationshipPosition:
    """Convert RelationshipPositionData dataclass to RelationshipPosition ORM model"""
    return RelationshipPosition(
        id=uuid.UUID(position_data.id) if position_data.id else None,
        relationship_id=uuid.UUID(position_data.relationship_id),
        security_id=uuid.UUID(position_data.security_id),
        position_date=position_data.position_date,
        shares_amount=position_data.shares_amount,
        direct_ownership=position_data.direct_ownership,
        ownership_nature_explanation=position_data.ownership_nature_explanation,
        filing_id=uuid.UUID(position_data.filing_id),
        transaction_id=uuid.UUID(position_data.transaction_id) if position_data.transaction_id else None,
        is_position_only=position_data.is_position_only,
        position_type=position_data.position_type,
        derivative_security_id=uuid.UUID(position_data.derivative_security_id) if position_data.derivative_security_id else None
    )

def convert_position_orm_to_data(position_orm: RelationshipPosition) -> RelationshipPositionData:
    """Convert RelationshipPosition ORM model to RelationshipPositionData dataclass"""
    return RelationshipPositionData(
        id=str(position_orm.id),
        relationship_id=str(position_orm.relationship_id),
        security_id=str(position_orm.security_id),
        position_date=position_orm.position_date,
        shares_amount=position_orm.shares_amount,
        direct_ownership=position_orm.direct_ownership,
        ownership_nature_explanation=position_orm.ownership_nature_explanation,
        filing_id=str(position_orm.filing_id),
        transaction_id=str(position_orm.transaction_id) if position_orm.transaction_id else None,
        is_position_only=position_orm.is_position_only,
        position_type=position_orm.position_type,
        derivative_security_id=str(position_orm.derivative_security_id) if position_orm.derivative_security_id else None
    )
```

## Service Implementation

```python
# services/forms/position_service.py
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import date, timedelta
from decimal import Decimal

from models.orm_models.forms.relationship_position_orm import RelationshipPosition
from models.dataclasses.forms.position_data import RelationshipPositionData
from models.adapters.position_adapter import (
    convert_position_data_to_orm,
    convert_position_orm_to_data
)
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from services.forms.transaction_service import TransactionService

class PositionService:
    """Service for managing Form 4 relationship positions"""
    
    def __init__(self, db_session: Session, transaction_service: Optional[TransactionService] = None):
        self.db_session = db_session
        self.transaction_service = transaction_service or TransactionService(db_session)
    
    def create_position(self, position_data: RelationshipPositionData) -> str:
        """Create a new relationship position"""
        position = convert_position_data_to_orm(position_data)
        self.db_session.add(position)
        self.db_session.flush()  # Generate ID without committing
        
        return str(position.id)
    
    def get_position(self, position_id: str) -> Optional[RelationshipPositionData]:
        """Get a position by ID"""
        position = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.id == position_id
        ).first()
        
        if not position:
            return None
        
        return convert_position_orm_to_data(position)
    
    def get_latest_position(self, relationship_id: str, security_id: str, 
                            derivative_security_id: Optional[str] = None, 
                            as_of_date: Optional[date] = None) -> Optional[RelationshipPositionData]:
        """Get the latest position for a relationship-security combination as of a specific date"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id,
            RelationshipPosition.security_id == security_id
        )
        
        if derivative_security_id:
            query = query.filter(RelationshipPosition.derivative_security_id == derivative_security_id)
        else:
            query = query.filter(RelationshipPosition.derivative_security_id.is_(None))
        
        if as_of_date:
            query = query.filter(RelationshipPosition.position_date <= as_of_date)
        
        position = query.order_by(desc(RelationshipPosition.position_date)).first()
        
        if not position:
            return None
        
        return convert_position_orm_to_data(position)
    
    def get_positions_for_relationship(self, relationship_id: str, 
                                     as_of_date: Optional[date] = None) -> List[RelationshipPositionData]:
        """Get all positions for a specific relationship"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id
        )
        
        if as_of_date:
            # Subquery to get the latest position for each security as of the date
            subquery = self.db_session.query(
                RelationshipPosition.security_id,
                RelationshipPosition.derivative_security_id,
                RelationshipPosition.direct_ownership,
                func.max(RelationshipPosition.position_date).label("max_date")
            ).filter(
                RelationshipPosition.relationship_id == relationship_id,
                RelationshipPosition.position_date <= as_of_date
            ).group_by(
                RelationshipPosition.security_id,
                RelationshipPosition.derivative_security_id,
                RelationshipPosition.direct_ownership
            ).subquery()
            
            # Join with the subquery to get the latest positions
            query = self.db_session.query(RelationshipPosition).join(
                subquery,
                and_(
                    RelationshipPosition.security_id == subquery.c.security_id,
                    RelationshipPosition.position_date == subquery.c.max_date,
                    RelationshipPosition.derivative_security_id == subquery.c.derivative_security_id,
                    RelationshipPosition.direct_ownership == subquery.c.direct_ownership
                )
            )
        
        positions = query.order_by(
            RelationshipPosition.position_date.desc(),
            RelationshipPosition.security_id,
            RelationshipPosition.derivative_security_id
        ).all()
        
        return [convert_position_orm_to_data(p) for p in positions]
    
    def get_positions_for_security(self, security_id: str, 
                                 as_of_date: Optional[date] = None) -> List[RelationshipPositionData]:
        """Get all positions for a specific security"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.security_id == security_id
        )
        
        if as_of_date:
            # Similar subquery approach for latest positions
            subquery = self.db_session.query(
                RelationshipPosition.relationship_id,
                RelationshipPosition.direct_ownership,
                func.max(RelationshipPosition.position_date).label("max_date")
            ).filter(
                RelationshipPosition.security_id == security_id,
                RelationshipPosition.position_date <= as_of_date
            ).group_by(
                RelationshipPosition.relationship_id,
                RelationshipPosition.direct_ownership
            ).subquery()
            
            query = self.db_session.query(RelationshipPosition).join(
                subquery,
                and_(
                    RelationshipPosition.relationship_id == subquery.c.relationship_id,
                    RelationshipPosition.position_date == subquery.c.max_date,
                    RelationshipPosition.direct_ownership == subquery.c.direct_ownership
                )
            )
        
        positions = query.order_by(
            RelationshipPosition.position_date.desc(),
            RelationshipPosition.relationship_id
        ).all()
        
        return [convert_position_orm_to_data(p) for p in positions]
    
    def update_position_from_transaction(self, transaction: Union[NonDerivativeTransactionData, DerivativeTransactionData]) -> str:
        """Create or update a position based on a transaction"""
        # Determine transaction type
        is_derivative = isinstance(transaction, DerivativeTransactionData)
        position_type = 'derivative' if is_derivative else 'equity'
        derivative_security_id = getattr(transaction, 'derivative_security_id', None) if is_derivative else None
        
        # Try to find the latest position
        latest_position = self.get_latest_position(
            relationship_id=transaction.relationship_id,
            security_id=transaction.security_id,
            derivative_security_id=derivative_security_id,
            as_of_date=transaction.transaction_date - timedelta(days=1)  # Latest position before transaction
        )
        
        # Calculate new position amount
        new_amount = transaction.position_impact
        if latest_position:
            new_amount += latest_position.shares_amount
        
        # Create new position
        position_data = RelationshipPositionData(
            relationship_id=transaction.relationship_id,
            security_id=transaction.security_id,
            position_date=transaction.transaction_date,
            shares_amount=new_amount,
            direct_ownership=transaction.direct_ownership,
            ownership_nature_explanation=transaction.ownership_nature_explanation,
            filing_id=transaction.form4_filing_id,
            transaction_id=transaction.id,
            is_position_only=False,
            position_type=position_type,
            derivative_security_id=derivative_security_id
        )
        
        return self.create_position(position_data)
    
    def create_position_only_entry(self, position_data: RelationshipPositionData) -> str:
        """Create a position-only entry (from a holding without transaction)"""
        # Set position-only flag
        position_data.is_position_only = True
        
        # Check for duplicate position-only entries
        existing = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == position_data.relationship_id,
            RelationshipPosition.security_id == position_data.security_id,
            RelationshipPosition.position_date == position_data.position_date,
            RelationshipPosition.derivative_security_id == (
                uuid.UUID(position_data.derivative_security_id) 
                if position_data.derivative_security_id else None
            ),
            RelationshipPosition.direct_ownership == position_data.direct_ownership,
            RelationshipPosition.is_position_only == True
        ).first()
        
        if existing:
            # Update existing entry
            existing.shares_amount = position_data.shares_amount
            existing.ownership_nature_explanation = position_data.ownership_nature_explanation
            existing.filing_id = uuid.UUID(position_data.filing_id)
            self.db_session.flush()
            return str(existing.id)
        
        # Create new position
        return self.create_position(position_data)
    
    def get_position_history(self, relationship_id: str, security_id: str,
                           derivative_security_id: Optional[str] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[RelationshipPositionData]:
        """Get position history for a relationship-security combination"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id,
            RelationshipPosition.security_id == security_id
        )
        
        if derivative_security_id:
            query = query.filter(RelationshipPosition.derivative_security_id == derivative_security_id)
        else:
            query = query.filter(RelationshipPosition.derivative_security_id.is_(None))
        
        if start_date:
            query = query.filter(RelationshipPosition.position_date >= start_date)
        
        if end_date:
            query = query.filter(RelationshipPosition.position_date <= end_date)
        
        positions = query.order_by(RelationshipPosition.position_date).all()
        
        return [convert_position_orm_to_data(p) for p in positions]
    
    def calculate_total_shares_owned(self, relationship_id: str, 
                                   as_of_date: Optional[date] = None) -> Dict[str, Decimal]:
        """Calculate total shares owned per security for a relationship"""
        positions = self.get_positions_for_relationship(relationship_id, as_of_date)
        
        # Group by security_id and sum shares
        totals = {}
        for position in positions:
            security_id = position.security_id
            if security_id not in totals:
                totals[security_id] = Decimal('0')
            
            totals[security_id] += position.shares_amount
        
        return totals
    
    def recalculate_positions(self, relationship_id: str, security_id: str,
                            start_date: Optional[date] = None) -> None:
        """Recalculate positions for a relationship-security combination"""
        # Get transactions in chronological order
        if start_date:
            non_derivative = self.transaction_service.get_transactions_for_security(
                security_id, start_date=start_date
            )
            
            # Also get derivative transactions if applicable
            derivative = []
            derivative_securities = self.db_session.query(DerivativeSecurity).filter(
                DerivativeSecurity.underlying_security_id == security_id
            ).all()
            
            for deriv_sec in derivative_securities:
                deriv_txs = self.transaction_service.get_transactions_for_derivative_security(
                    str(deriv_sec.id), start_date=start_date
                )
                derivative.extend(deriv_txs)
        else:
            # Get all transactions for the relationship
            non_derivative, derivative = self.transaction_service.get_transactions_for_relationship(relationship_id)
            
            # Filter by security_id
            non_derivative = [tx for tx in non_derivative if tx.security_id == security_id]
            derivative = [tx for tx in derivative if tx.security_id == security_id]
        
        # Combine and sort by date
        all_transactions = []
        all_transactions.extend(non_derivative)
        all_transactions.extend(derivative)
        all_transactions.sort(key=lambda tx: tx.transaction_date)
        
        # Delete existing positions that will be recalculated
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id,
            RelationshipPosition.security_id == security_id,
            RelationshipPosition.is_position_only == False
        )
        
        if start_date:
            query = query.filter(RelationshipPosition.position_date >= start_date)
            
        query.delete(synchronize_session=False)
        
        # Process transactions in order
        for transaction in all_transactions:
            if transaction.relationship_id == relationship_id:
                self.update_position_from_transaction(transaction)
        
        self.db_session.flush()
```

## Migration Script

```sql
-- migration/V22__create_position_table.sql

-- Relationship positions table for tracking current positions
CREATE TABLE IF NOT EXISTS public.relationship_positions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    position_date date NOT NULL,
    shares_amount numeric NOT NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    filing_id uuid NOT NULL,
    transaction_id uuid NULL,
    is_position_only boolean DEFAULT false NOT NULL,
    position_type text NOT NULL, -- 'equity' or 'derivative'
    derivative_security_id uuid NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT relationship_positions_pkey PRIMARY KEY (id),
    CONSTRAINT relationship_positions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_filing_fkey FOREIGN KEY (filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_derivative_fkey FOREIGN KEY (derivative_security_id) 
        REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT position_type_check CHECK (position_type IN ('equity', 'derivative'))
);

-- Create indexes for relationship positions
CREATE INDEX IF NOT EXISTS idx_relationship_positions_relationship ON public.relationship_positions USING btree (relationship_id);
CREATE INDEX IF NOT EXISTS idx_relationship_positions_security ON public.relationship_positions USING btree (security_id);
CREATE INDEX IF NOT EXISTS idx_relationship_positions_date ON public.relationship_positions USING btree (position_date);
CREATE INDEX IF NOT EXISTS idx_relationship_positions_derivative ON public.relationship_positions USING btree (derivative_security_id);
CREATE INDEX IF NOT EXISTS idx_relationship_positions_filing ON public.relationship_positions USING btree (filing_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_relationship_position_unique ON public.relationship_positions USING btree (relationship_id, security_id, position_date, derivative_security_id, direct_ownership) WHERE (is_position_only = true);
```

## Unit Tests

The unit tests for the position service should follow the approach used in Phase 2, using mock-based testing to avoid circular dependencies.

## Integration with Transaction Processing

The position system should be integrated with transaction processing so that positions are automatically updated when transactions are created. This can be done by:

1. Extending the TransactionService to call PositionService.update_position_from_transaction when a transaction is created
2. Implementing a Form4Parser update to handle position-only entries (holdings without transactions)
3. Creating a CLI tool for recalculating positions

## Next Steps After Phase 3

1. **Transaction Integration**:
   - Update the Form4Parser to use the SecurityService, TransactionService, and PositionService
   - Ensure backward compatibility with existing data

2. **Data Migration**:
   - Create migration tools to populate the new tables from the existing form4_transactions table
   - Implement position recalculation for historical data

3. **Documentation and Reporting**:
   - Update READMEs in relevant folders
   - Document the position tracking approach
   - Create reporting utilities for position analysis
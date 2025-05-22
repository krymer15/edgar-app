# Phase 1: Security Normalization Implementation (FOR IMPLEMENTATION)

This document outlines the specific implementation details for Phase 1 of the Form 4 schema redesign: Security Normalization. This phase focuses on creating the foundation for the new schema by establishing the normalized security tables and related functionality.

## Database Schema

### Core Tables to Create

```sql
-- Securities table for normalized security information
CREATE TABLE public.securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    issuer_entity_id uuid NOT NULL,
    security_type text NOT NULL, -- 'equity', 'option', 'convertible', 'other_derivative'
    standard_cusip text NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT securities_pkey PRIMARY KEY (id),
    CONSTRAINT securities_issuer_entity_fkey FOREIGN KEY (issuer_entity_id) 
        REFERENCES public.entities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT security_type_check CHECK (security_type IN 
        ('equity', 'option', 'convertible', 'other_derivative'))
);
CREATE INDEX idx_securities_issuer ON public.securities USING btree (issuer_entity_id);
CREATE INDEX idx_securities_title ON public.securities USING btree (title);

-- Derivative securities table for derivative-specific details  
CREATE TABLE public.derivative_securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    underlying_security_id uuid NULL,
    underlying_security_title text NOT NULL,
    conversion_price numeric NULL,
    exercise_date date NULL,
    expiration_date date NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_securities_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_securities_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_securities_underlying_fkey FOREIGN KEY (underlying_security_id) 
        REFERENCES public.securities(id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE INDEX idx_derivative_underlying ON public.derivative_securities USING btree (underlying_security_id);
```

## SQLAlchemy ORM Models

### Security ORM Model

```python
# models/orm_models/forms/security_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Security(Base):
    __tablename__ = "securities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    security_type = Column(String, nullable=False)
    standard_cusip = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_securities_issuer', 'issuer_entity_id'),
        Index('idx_securities_title', 'title'),
        CheckConstraint("security_type IN ('equity', 'option', 'convertible', 'other_derivative')",
                      name="security_type_check"),
    )

    # Relationships
    issuer_entity = relationship("Entity", foreign_keys=[issuer_entity_id])
    derivative_security = relationship("DerivativeSecurity", back_populates="security", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Security(id='{self.id}', title='{self.title}', type='{self.security_type}')>"
```

### Derivative Security ORM Model

```python
# models/orm_models/forms/derivative_security_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class DerivativeSecurity(Base):
    __tablename__ = "derivative_securities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    underlying_security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="SET NULL", onupdate="CASCADE"))
    underlying_security_title = Column(String, nullable=False)
    conversion_price = Column(Numeric)
    exercise_date = Column(Date)
    expiration_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_derivative_underlying', 'underlying_security_id'),
    )

    # Relationships
    security = relationship("Security", foreign_keys=[security_id], back_populates="derivative_security")
    underlying_security = relationship("Security", foreign_keys=[underlying_security_id])

    def __repr__(self):
        return f"<DerivativeSecurity(id='{self.id}', security_id='{self.security_id}')>"
```

## Dataclass Models

### Security Dataclass

```python
# models/dataclasses/forms/security_data.py
from dataclasses import dataclass
from typing import Optional
import uuid

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

### Derivative Security Dataclass

```python
# models/dataclasses/forms/derivative_security_data.py
from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal
import uuid

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
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
```

## Adapter Implementation

```python
# models/adapters/security_adapter.py
import uuid
from typing import List, Optional, Dict

from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.orm_models.forms.security_orm import Security
from models.orm_models.forms.derivative_security_orm import DerivativeSecurity

def convert_security_data_to_orm(security_data: SecurityData) -> Security:
    """Convert SecurityData dataclass to Security ORM model"""
    return Security(
        id=uuid.UUID(security_data.id) if security_data.id else None,
        title=security_data.title,
        issuer_entity_id=uuid.UUID(security_data.issuer_entity_id),
        security_type=security_data.security_type,
        standard_cusip=security_data.standard_cusip
    )

def convert_security_orm_to_data(security_orm: Security) -> SecurityData:
    """Convert Security ORM model to SecurityData dataclass"""
    return SecurityData(
        id=str(security_orm.id),
        title=security_orm.title,
        issuer_entity_id=str(security_orm.issuer_entity_id),
        security_type=security_orm.security_type,
        standard_cusip=security_orm.standard_cusip
    )

def convert_derivative_security_data_to_orm(derivative_data: DerivativeSecurityData) -> DerivativeSecurity:
    """Convert DerivativeSecurityData dataclass to DerivativeSecurity ORM model"""
    return DerivativeSecurity(
        id=uuid.UUID(derivative_data.id) if derivative_data.id else None,
        security_id=uuid.UUID(derivative_data.security_id),
        underlying_security_id=uuid.UUID(derivative_data.underlying_security_id) if derivative_data.underlying_security_id else None,
        underlying_security_title=derivative_data.underlying_security_title,
        conversion_price=derivative_data.conversion_price,
        exercise_date=derivative_data.exercise_date,
        expiration_date=derivative_data.expiration_date
    )

def convert_derivative_security_orm_to_data(derivative_orm: DerivativeSecurity) -> DerivativeSecurityData:
    """Convert DerivativeSecurity ORM model to DerivativeSecurityData dataclass"""
    return DerivativeSecurityData(
        id=str(derivative_orm.id),
        security_id=str(derivative_orm.security_id),
        underlying_security_id=str(derivative_orm.underlying_security_id) if derivative_orm.underlying_security_id else None,
        underlying_security_title=derivative_orm.underlying_security_title,
        conversion_price=derivative_orm.conversion_price,
        exercise_date=derivative_orm.exercise_date,
        expiration_date=derivative_orm.expiration_date
    )
```

## Service Implementation

```python
# services/forms/security_service.py
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.orm_models.forms.security_orm import Security
from models.orm_models.forms.derivative_security_orm import DerivativeSecurity
from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.adapters.security_adapter import (
    convert_security_data_to_orm,
    convert_security_orm_to_data,
    convert_derivative_security_data_to_orm,
    convert_derivative_security_orm_to_data
)

class SecurityService:
    """Service for managing securities"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_or_create_security(self, security_data: SecurityData) -> str:
        """Get existing security or create a new one, return the ID"""
        # Check if security exists
        security = self.db_session.query(Security).filter(
            Security.title == security_data.title,
            Security.issuer_entity_id == security_data.issuer_entity_id
        ).first()
        
        if security:
            return str(security.id)
        
        # Create new security
        new_security = convert_security_data_to_orm(security_data)
        self.db_session.add(new_security)
        self.db_session.flush()  # Generate ID without committing
        
        return str(new_security.id)
    
    def get_securities_for_issuer(self, issuer_entity_id: str) -> List[SecurityData]:
        """Get all securities for an issuer"""
        securities = self.db_session.query(Security).filter(
            Security.issuer_entity_id == issuer_entity_id
        ).all()
        
        return [convert_security_orm_to_data(security) for security in securities]
    
    def get_or_create_derivative_security(self, derivative_data: DerivativeSecurityData) -> str:
        """Get existing derivative security or create a new one, return the ID"""
        # Check if derivative security exists
        derivative = self.db_session.query(DerivativeSecurity).filter(
            DerivativeSecurity.security_id == derivative_data.security_id,
            DerivativeSecurity.underlying_security_title == derivative_data.underlying_security_title,
            DerivativeSecurity.conversion_price == derivative_data.conversion_price
            # Not including exercise/expiration dates as they might not be unique identifiers
        ).first()
        
        if derivative:
            return str(derivative.id)
        
        # Create new derivative security
        new_derivative = convert_derivative_security_data_to_orm(derivative_data)
        self.db_session.add(new_derivative)
        self.db_session.flush()  # Generate ID without committing
        
        return str(new_derivative.id)
    
    def find_security_by_title_and_issuer(self, title: str, issuer_entity_id: str) -> Optional[SecurityData]:
        """Find a security by title and issuer"""
        security = self.db_session.query(Security).filter(
            Security.title == title,
            Security.issuer_entity_id == issuer_entity_id
        ).first()
        
        if not security:
            return None
            
        return convert_security_orm_to_data(security)
    
    def get_derivative_security(self, derivative_id: str) -> Optional[DerivativeSecurityData]:
        """Get a derivative security by ID"""
        derivative = self.db_session.query(DerivativeSecurity).filter(
            DerivativeSecurity.id == derivative_id
        ).first()
        
        if not derivative:
            return None
            
        return convert_derivative_security_orm_to_data(derivative)
```

## Unit Tests

```python
# tests/forms/test_security_service.py
import pytest
from uuid import UUID
from datetime import date
from decimal import Decimal

from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from services.forms.security_service import SecurityService

@pytest.fixture
def security_service(db_session):
    return SecurityService(db_session)

def test_get_or_create_security_creates_new(security_service, db_session):
    # Setup
    issuer_id = str(UUID('12345678-1234-5678-1234-567812345678'))
    security_data = SecurityData(
        title="Common Stock",
        issuer_entity_id=issuer_id,
        security_type="equity"
    )
    
    # Execute
    security_id = security_service.get_or_create_security(security_data)
    
    # Verify
    assert security_id is not None
    assert UUID(security_id)  # Validates it's a UUID string
    
    # Check that it was persisted
    from models.orm_models.forms.security_orm import Security
    security = db_session.query(Security).filter(Security.id == security_id).first()
    assert security is not None
    assert security.title == "Common Stock"
    assert security.issuer_entity_id == UUID(issuer_id)
    assert security.security_type == "equity"

def test_get_or_create_security_finds_existing(security_service, db_session):
    # Setup
    issuer_id = str(UUID('12345678-1234-5678-1234-567812345678'))
    security_data = SecurityData(
        title="Common Stock",
        issuer_entity_id=issuer_id,
        security_type="equity"
    )
    
    # Create first instance
    first_id = security_service.get_or_create_security(security_data)
    
    # Execute - try to create again
    second_id = security_service.get_or_create_security(security_data)
    
    # Verify - should return same ID
    assert second_id == first_id
    
    # Check count in database - should still be just one
    from models.orm_models.forms.security_orm import Security
    count = db_session.query(Security).filter(
        Security.title == "Common Stock",
        Security.issuer_entity_id == UUID(issuer_id)
    ).count()
    assert count == 1

def test_create_derivative_security(security_service, db_session):
    # Setup - create parent security first
    issuer_id = str(UUID('12345678-1234-5678-1234-567812345678'))
    security_data = SecurityData(
        title="Stock Option (Right to Buy)",
        issuer_entity_id=issuer_id,
        security_type="option"
    )
    security_id = security_service.get_or_create_security(security_data)
    
    # Now create derivative security
    derivative_data = DerivativeSecurityData(
        security_id=security_id,
        underlying_security_title="Common Stock",
        conversion_price=Decimal("10.50"),
        exercise_date=date(2023, 5, 15),
        expiration_date=date(2028, 5, 15)
    )
    
    # Execute
    derivative_id = security_service.get_or_create_derivative_security(derivative_data)
    
    # Verify
    assert derivative_id is not None
    assert UUID(derivative_id)  # Validates it's a UUID string
    
    # Check that it was persisted
    from models.orm_models.forms.derivative_security_orm import DerivativeSecurity
    derivative = db_session.query(DerivativeSecurity).filter(
        DerivativeSecurity.id == derivative_id
    ).first()
    assert derivative is not None
    assert derivative.security_id == UUID(security_id)
    assert derivative.underlying_security_title == "Common Stock"
    assert derivative.conversion_price == Decimal("10.50")
    assert derivative.exercise_date == date(2023, 5, 15)
    assert derivative.expiration_date == date(2028, 5, 15)
```

## Migration Script

```sql
-- migration/V20__create_securities_tables.sql

-- Create securities table
CREATE TABLE IF NOT EXISTS public.securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    issuer_entity_id uuid NOT NULL,
    security_type text NOT NULL,
    standard_cusip text NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT securities_pkey PRIMARY KEY (id),
    CONSTRAINT securities_issuer_entity_fkey FOREIGN KEY (issuer_entity_id) 
        REFERENCES public.entities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT security_type_check CHECK (security_type IN 
        ('equity', 'option', 'convertible', 'other_derivative'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_securities_issuer ON public.securities USING btree (issuer_entity_id);
CREATE INDEX IF NOT EXISTS idx_securities_title ON public.securities USING btree (title);

-- Create derivative securities table
CREATE TABLE IF NOT EXISTS public.derivative_securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    underlying_security_id uuid NULL,
    underlying_security_title text NOT NULL,
    conversion_price numeric NULL,
    exercise_date date NULL,
    expiration_date date NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_securities_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_securities_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_securities_underlying_fkey FOREIGN KEY (underlying_security_id) 
        REFERENCES public.securities(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Create index on underlying security
CREATE INDEX IF NOT EXISTS idx_derivative_underlying ON public.derivative_securities USING btree (underlying_security_id);

-- Initial data migration - populate securities from existing transactions
INSERT INTO securities (title, issuer_entity_id, security_type, created_at, updated_at)
SELECT DISTINCT 
    t.security_title as title,
    r.issuer_entity_id,
    CASE WHEN t.is_derivative THEN 
        CASE 
            WHEN t.security_title ILIKE '%option%' THEN 'option'
            WHEN t.security_title ILIKE '%convert%' THEN 'convertible'
            ELSE 'other_derivative'
        END
    ELSE 'equity' END as security_type,
    t.created_at,
    t.updated_at
FROM form4_transactions t
JOIN form4_relationships r ON t.relationship_id = r.id
ON CONFLICT DO NOTHING;

-- Create a temporary mapping table for derivative security creation
CREATE TEMPORARY TABLE temp_derivative_mapping AS
SELECT DISTINCT
    s.id as security_id,
    t.underlying_security_shares,
    t.conversion_price,
    t.exercise_date,
    t.expiration_date,
    COALESCE(t.security_title, 'Common Stock') as underlying_security_title
FROM form4_transactions t
JOIN form4_relationships r ON t.relationship_id = r.id
JOIN securities s ON s.title = t.security_title AND s.issuer_entity_id = r.issuer_entity_id
WHERE t.is_derivative = true;

-- Populate derivative securities
INSERT INTO derivative_securities (security_id, underlying_security_title, conversion_price, exercise_date, expiration_date)
SELECT 
    security_id,
    underlying_security_title,
    conversion_price,
    exercise_date,
    expiration_date
FROM temp_derivative_mapping
ON CONFLICT DO NOTHING;

-- Drop the temporary table
DROP TABLE temp_derivative_mapping;
```

## Next Steps

After implementing Phase 1:

1. **Testing**:
   - Run all unit tests to verify security handling
   - Test with real Form 4 XML data to ensure correct security extraction
   - Test the migration script on a copy of production data

2. **Documentation**:
   - Update README files in the relevant folders
   - Document the new security normalization approach
   - Create documentation for the security service

3. **Phase 2 Preparation**:
   - Plan the transaction table creation
   - Prepare for implementing transaction-related dataclasses and services
   - Design the migration strategy for transaction data
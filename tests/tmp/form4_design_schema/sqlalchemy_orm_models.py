# 1. Security Model

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
    non_derivative_transactions = relationship("NonDerivativeTransaction", back_populates="security", cascade="all, delete-orphan")
    derivative_transactions = relationship("DerivativeTransaction", back_populates="security", cascade="all, delete-orphan")
    positions = relationship("RelationshipPosition", back_populates="security", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Security(id='{self.id}', title='{self.title}', type='{self.security_type}')>"

# 2. Derivative Security Model

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
    derivative_transactions = relationship("DerivativeTransaction", back_populates="derivative_security", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DerivativeSecurity(id='{self.id}', title='{self.security.title if self.security else None}')>"

# 3. Relationship Position Model

# models/orm_models/forms/relationship_position_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

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
    transaction_id = Column(UUID(as_uuid=True)) # Generic transaction ID reference, could be derivative or non-derivative
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_relationship_positions_relationship', 'relationship_id'),
        Index('idx_relationship_positions_security', 'security_id'),
        Index('idx_relationship_positions_date', 'position_date'),
    )

    # Relationships
    relationship = relationship("Form4Relationship", back_populates="positions")
    security = relationship("Security", back_populates="positions")
    filing = relationship("Form4Filing", backref="positions")

    def __repr__(self):
        return f"<RelationshipPosition(id='{self.id}', date='{self.position_date}', shares='{self.shares_amount}')>"

# 4. Non-Derivative Transaction Model

# models/orm_models/forms/non_derivative_transaction_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

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
    transaction_timeliness = Column(String)  # 'P' for on time, 'L' for late
    footnote_ids = Column(ARRAY(String))
    acquisition_disposition_flag = Column(String, nullable=False)
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
    filing = relationship("Form4Filing", back_populates="non_derivative_transactions")
    relationship = relationship("Form4Relationship", back_populates="non_derivative_transactions")
    security = relationship("Security", back_populates="non_derivative_transactions")

    def __repr__(self):
        return f"<NonDerivativeTransaction(id='{self.id}', code='{self.transaction_code}', date='{self.transaction_date}')>"

    @property
    def position_impact(self):
        """Calculate the impact on the position (positive for acquisitions, negative for dispositions)"""
        if self.acquisition_disposition_flag == 'A':
            return self.shares_amount
        elif self.acquisition_disposition_flag == 'D':
            return -1 * self.shares_amount
        return 0

# 5. Derivative Transaction Model

# models/orm_models/forms/derivative_transaction_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

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
    transaction_timeliness = Column(String)  # 'P' for on time, 'L' for late
    footnote_ids = Column(ARRAY(String))
    acquisition_disposition_flag = Column(String, nullable=False)
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
    filing = relationship("Form4Filing", back_populates="derivative_transactions")
    relationship = relationship("Form4Relationship", back_populates="derivative_transactions")
    security = relationship("Security", back_populates="derivative_transactions")
    derivative_security = relationship("DerivativeSecurity", back_populates="derivative_transactions")

    def __repr__(self):
        return f"<DerivativeTransaction(id='{self.id}', code='{self.transaction_code}', date='{self.transaction_date}')>"

    @property
    def position_impact(self):
        """Calculate the impact on the derivative position (positive for acquisitions, negative for dispositions)"""
        if self.acquisition_disposition_flag == 'A':
            return self.derivative_shares_amount
        elif self.acquisition_disposition_flag == 'D':
            return -1 * self.derivative_shares_amount
        return 0

# 6. Updated Form4Filing Model

# We need to update the Form4Filing model to add the new relationships:

# models/orm_models/forms/form4_filing_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Form4Filing(Base):
    __tablename__ = "form4_filings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accession_number = Column(String, ForeignKey("filing_metadata.accession_number", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True)
    period_of_report = Column(Date)
    has_multiple_owners = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    relationships = relationship("Form4Relationship", back_populates="form4_filing", cascade="all, delete-orphan")
    # Legacy relationship, will be used during migration
    transactions = relationship("Form4Transaction", back_populates="form4_filing", cascade="all, delete-orphan")
    # New relationships
    non_derivative_transactions = relationship("NonDerivativeTransaction", back_populates="filing", cascade="all, delete-orphan")
    derivative_transactions = relationship("DerivativeTransaction", back_populates="filing", cascade="all, delete-orphan")
    # Position relationship is defined on RelationshipPosition

    def __repr__(self):
        return f"<Form4Filing(id='{self.id}', accession_number='{self.accession_number}')>"

# 7. Updated Form4Relationship Model

# We need to update the Form4Relationship model to add the new relationships:

# models/orm_models/forms/form4_relationship_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, JSON, CheckConstraint, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Form4Relationship(Base):
    __tablename__ = "form4_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    owner_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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
    # This is kept for backward compatibility and will be calculated from positions
    total_shares_owned = Column(Numeric)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        CheckConstraint(
            "relationship_type IN ('director', 'officer', '10_percent_owner', 'other')",
            name="relationship_type_check"
        ),
        Index('idx_form4_relationships_filing_id', 'form4_filing_id'),
        Index('idx_form4_relationships_issuer', 'issuer_entity_id'),
        Index('idx_form4_relationships_owner', 'owner_entity_id'),
        Index('idx_form4_relationships_total_shares', 'total_shares_owned'),
    )

    # Relationships
    form4_filing = relationship("Form4Filing", back_populates="relationships")
    issuer_entity = relationship("Entity", foreign_keys=[issuer_entity_id], back_populates="issuer_relationships")
    owner_entity = relationship("Entity", foreign_keys=[owner_entity_id], back_populates="owner_relationships")
    # Legacy relationship, will be used during migration
    transactions = relationship("Form4Transaction", back_populates="relationship", cascade="all, delete-orphan")
    # New relationships
    non_derivative_transactions = relationship("NonDerivativeTransaction", back_populates="relationship", cascade="all, delete-orphan")
    derivative_transactions = relationship("DerivativeTransaction", back_populates="relationship", cascade="all, delete-orphan")
    positions = relationship("RelationshipPosition", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form4Relationship(id='{self.id}', issuer='{self.issuer_entity_id}', owner='{self.owner_entity_id}')>"

    def get_current_position(self, security_id, as_of_date=None):
        """Get the current position for a specific security as of a given date"""
        from sqlalchemy import desc
        from datetime import date

        if as_of_date is None:
            as_of_date = date.today()

        # Find the most recent position for this security before or on the as_of_date
        return self.positions.query.filter(
            RelationshipPosition.security_id == security_id,
            RelationshipPosition.position_date <= as_of_date
        ).order_by(desc(RelationshipPosition.position_date)).first()
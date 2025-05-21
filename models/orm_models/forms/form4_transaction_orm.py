# models/orm_models/forms/form4_transaction_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Form4Transaction(Base):
    __tablename__ = "form4_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("form4_filings.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("form4_relationships.id", ondelete="CASCADE", onupdate="CASCADE"),
nullable=False)
    transaction_code = Column(String)  # Nullable for position-only rows
    transaction_date = Column(Date)    # Nullable for position-only rows (Bug 10 fix)
    security_title = Column(String, nullable=False)
    transaction_form_type = Column(String)
    shares_amount = Column(Numeric)    # Column 4 for transactions, Column 5 for positions
    price_per_share = Column(Numeric)
    ownership_nature = Column(String)  # 'D' for Direct or 'I' for Indirect
    indirect_ownership_explanation = Column(String)  # Added field
    is_derivative = Column(Boolean, nullable=False, default=False)
    equity_swap_involved = Column(Boolean, default=False)
    transaction_timeliness = Column(String)  # 'P' for on time, 'L' for late
    footnote_ids = Column(ARRAY(String))
    acquisition_disposition_flag = Column(String)  # 'A' for Acquisition or 'D' for Disposition
    
    # Bug 10 Fix: Add is_position_only flag
    is_position_only = Column(Boolean, default=False)  # True for holding entries with no transaction
    underlying_security_shares = Column(Numeric)  # For derivative holdings

    # Added derivative-specific fields
    conversion_price = Column(Numeric)
    exercise_date = Column(Date)
    expiration_date = Column(Date)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Table arguments
    __table_args__ = (
        Index('idx_form4_transactions_filing_id', 'form4_filing_id'),
        Index('idx_form4_transactions_relationship_id', 'relationship_id'),
        CheckConstraint("ownership_nature IN ('D', 'I') OR ownership_nature IS NULL",
                        name="ownership_nature_check"),
        CheckConstraint("acquisition_disposition_flag IN ('A', 'D') OR acquisition_disposition_flag IS NULL",
                        name="acquisition_disposition_flag_check"),
    )

    # Relationships
    form4_filing = relationship("Form4Filing", back_populates="transactions")
    relationship = relationship("Form4Relationship", back_populates="transactions")

    def __repr__(self):
        return f"<Form4Transaction(id='{self.id}', code='{self.transaction_code}', date='{self.transaction_date}')>"

    @classmethod
    def get_transactions_for_filing(cls, session, filing_id):
        """Get all transactions for a specific filing"""
        return session.query(cls).filter(cls.form4_filing_id == filing_id).all()

    @property
    def is_purchase(self):
        """Helper method to determine if this is a purchase transaction"""
        return self.transaction_code in ('P', 'A')

    @property
    def is_sale(self):
        """Helper method to determine if this is a sale transaction"""
        return self.transaction_code in ('S', 'D')
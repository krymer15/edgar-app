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
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
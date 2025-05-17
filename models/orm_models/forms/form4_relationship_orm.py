# models/orm_models/forms/form4_relationship_orm.py

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, JSON, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB  # Using JSONB is better
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
    relationship_details = Column(JSONB)  # JSONB for better performance
    is_group_filing = Column(Boolean, default=False)
    filing_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Table arguments
    __table_args__ = (
        CheckConstraint(
            "relationship_type IN ('director', 'officer', '10_percent_owner', 'other')",
            name="relationship_type_check"
        ),
        Index('idx_form4_relationships_filing_id', 'form4_filing_id'),
        Index('idx_form4_relationships_issuer', 'issuer_entity_id'),
        Index('idx_form4_relationships_owner', 'owner_entity_id'),
    )

    # Relationships
    form4_filing = relationship("Form4Filing", back_populates="relationships")
    issuer_entity = relationship("Entity", foreign_keys=[issuer_entity_id], back_populates="issuer_relationships")
    owner_entity = relationship("Entity", foreign_keys=[owner_entity_id], back_populates="owner_relationships")
    transactions = relationship("Form4Transaction", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form4Relationship(id='{self.id}', issuer='{self.issuer_entity_id}', owner='{self.owner_entity_id}')>"

    @classmethod
    def find_by_entities(cls, session, filing_id, issuer_id, owner_id):
        """Find relationship by filing, issuer and owner IDs"""
        return session.query(cls).filter(
            cls.form4_filing_id == filing_id,
            cls.issuer_entity_id == issuer_id,
            cls.owner_entity_id == owner_id
        ).first()
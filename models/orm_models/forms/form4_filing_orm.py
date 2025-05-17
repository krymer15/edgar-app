# models/orm_models/forms/form4_filing_orm.py  # Updated path for organization

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Form4Filing(Base):
    __tablename__ = "form4_filings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accession_number = Column(
        String, 
        ForeignKey("filing_metadata.accession_number", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False, 
        unique=True)
    period_of_report = Column(Date)
    has_multiple_owners = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Add index definition to match the SQL migration
    __table_args__ = (
        Index('idx_form4_filings_accession', 'accession_number'),
    )

    # Relationships
    filing_metadata = relationship("FilingMetadata", back_populates="form4_filing")
    relationships = relationship("Form4Relationship", back_populates="form4_filing", cascade="all, delete-orphan")
    transactions = relationship("Form4Transaction", back_populates="form4_filing", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form4Filing(id='{self.id}', accession='{self.accession_number}')>"

    @classmethod
    def get_by_accession(cls, session, accession_number):
        """Get a Form4Filing by accession number"""
        return session.query(cls).filter(cls.accession_number == accession_number).first()
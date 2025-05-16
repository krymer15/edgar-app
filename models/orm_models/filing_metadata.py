# models/orm_models/filing_metadata.py

### mirrors DDL in `sql/create/crawler_idx/filing_metadata.sql`` ###

from sqlalchemy import Column, String, Date, TIMESTAMP, text, Text, Enum
from sqlalchemy.orm import relationship
from models.base import Base
from models.orm_models.filing_document_orm import FilingDocumentORM

class FilingMetadata(Base):
    __tablename__ = "filing_metadata"

    accession_number        = Column(Text, primary_key=True)
    cik                     = Column(Text, nullable=False, index=True)
    form_type               = Column(Text, nullable=False)
    filing_date             = Column(Date, nullable=False)
    filing_url              = Column(Text, nullable=True)
    created_at              = Column(
                                TIMESTAMP(timezone=True),
                                server_default=text("CURRENT_TIMESTAMP"),
                                nullable=True
                            )
    updated_at              = Column(
                                TIMESTAMP(timezone=True),
                                server_default=text("CURRENT_TIMESTAMP"),
                                onupdate=text("CURRENT_TIMESTAMP"),
                                nullable=True
                            )
    processing_status       = Column(Enum('pending', 'processing', 'completed', 'failed', 'skipped', 
                                name='processing_status_enum'), nullable=True)
    processing_started_at   = Column(TIMESTAMP(timezone=True), nullable=True)
    processing_completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    processing_error        = Column(Text, nullable=True)
    job_id                  = Column(String(36), nullable=True, index=True)
    last_updated_by         = Column(String(100), nullable=True)
    
    documents = relationship(
        "FilingDocumentORM",
        back_populates="filing",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<FilingMetadata "
            f"cik={self.cik} accession={self.accession_number} "
            f"form_type={self.form_type}>"
        )
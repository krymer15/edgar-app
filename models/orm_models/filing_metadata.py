# models/orm_models/filing_metadata.py

### mirrors DDL in `sql/create/crawler_idx/filing_metadata.sql`` ###

from sqlalchemy import Column, String, Date, TIMESTAMP, text, Text
from sqlalchemy.orm import relationship
from models.base import Base
from models.orm_models.filing_documents import FilingDocument

class FilingMetadata(Base):
    __tablename__ = "filing_metadata"

    accession_number = Column(Text, primary_key=True)
    cik              = Column(Text, nullable=False, index=True)
    form_type        = Column(Text, nullable=False)
    filing_date      = Column(Date, nullable=False)
    filing_url       = Column(Text, nullable=True)
    created_at       = Column(
                        TIMESTAMP(timezone=True),
                        server_default=text("CURRENT_TIMESTAMP"),
                        nullable=True
                     )
    updated_at       = Column(
                        TIMESTAMP(timezone=True),
                        server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=text("CURRENT_TIMESTAMP"),
                        nullable=True
                     )

    documents = relationship(
        "FilingDocument",
        back_populates="filing",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<FilingMetadata "
            f"cik={self.cik} accession={self.accession_number} "
            f"form_type={self.form_type}>"
        )

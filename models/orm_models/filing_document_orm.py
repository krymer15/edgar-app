# models/orm_models/filing_document.py

from sqlalchemy import Column, Text, Boolean, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models.base import Base
from uuid import uuid4 # for SQLite testing compatibility

class FilingDocumentORM(Base):
    '''
    The actual SQLAlchemy ORM class that defines the filing_documents table in Postgres.
    - convert_filing_doc_to_orm() in dataclass_to_orm.py converts a FilingDocumentRecord (DC) into a FilingDocument (ORM model)
      → see its use in FilingDocumentsWriter.
    '''
    __tablename__ = "filing_documents"

    id                = Column(
                          UUID(as_uuid=True),
                          primary_key=True,
                          default=uuid4, # used only by SQLAlchemy in tests (e.g., SQLite)
                          server_default=text("gen_random_uuid()"), # used by Postgres in production
                          nullable=False
                        )
    accession_number  = Column(
                          Text,
                          ForeignKey("filing_metadata.accession_number"),
                          nullable=False
                        )
    cik               = Column(Text, nullable=False)
    document_type     = Column(Text, nullable=True)
    filename          = Column(Text, nullable=True)
    description       = Column(Text, nullable=True)
    source_url        = Column(Text, nullable=True)
    source_type       = Column(Text, nullable=True)
    is_primary        = Column(Boolean,
                              server_default=text("false"),
                              nullable=False)
    is_exhibit        = Column(Boolean,
                              server_default=text("false"),
                              nullable=False)
    is_data_support   = Column(Boolean,
                              server_default=text("false"),
                              nullable=False)
    accessible        = Column(Boolean,
                              server_default=text("true"),
                              nullable=False)
    created_at        = Column(
                          TIMESTAMP(timezone=True),
                          server_default=text("CURRENT_TIMESTAMP"),
                          nullable=True
                       )
    updated_at        = Column(
                          TIMESTAMP(timezone=True),
                          server_default=text("CURRENT_TIMESTAMP"),
                          onupdate=text("CURRENT_TIMESTAMP"),
                          nullable=True
                       )

    filing = relationship("FilingMetadata", back_populates="documents")

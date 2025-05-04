# models/xml_metadata.py

import uuid
from sqlalchemy import Column, Text, Boolean, TIMESTAMP, ForeignKey, text, UniqueConstraint
from models.base import Base

class XmlMetadata(Base):
    __tablename__ = "xml_metadata"
    __table_args__ = (
        UniqueConstraint("accession_number", "filename", name="uq_accession_filename"),
    )

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    accession_number = Column(Text, ForeignKey("daily_index_metadata.accession_number"), nullable=False)
    cik = Column(Text, nullable=False)
    form_type = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    url = Column(Text, nullable=False)

    downloaded = Column(Boolean, default=False)
    parsed_successfully = Column(Boolean, default=False)
    source = Column(Text, default="embedded")  # optionally "exhibit"
    content_type = Column(Text, default="xml")

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

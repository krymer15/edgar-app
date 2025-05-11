import uuid
from sqlalchemy import Column, Text, Boolean, ForeignKey, TIMESTAMP, text
from models.base import Base

class ExhibitMetadata(Base):
    __tablename__ = "exhibit_metadata"

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4())) 
    accession_number = Column(Text, ForeignKey("parsed_sgml_metadata.accession_number"), nullable=False)

    filename = Column(Text)
    description = Column(Text)
    type = Column(Text)
    accessible = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

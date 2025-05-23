# models/parsed_sgml_metadata.py

from sqlalchemy import Column, Text, Date, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from models.base import Base
from models.daily_index_metadata import DailyIndexMetadata

class ParsedSgmlMetadata(Base):
    __tablename__ = "parsed_sgml_metadata"

    accession_number = mapped_column(
        Text, ForeignKey("daily_index_metadata.accession_number"), primary_key=True
    )
    parent_index = relationship("DailyIndexMetadata", back_populates="sgml_meta")

    primary_doc_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    form_type: Mapped[str] = mapped_column(Text, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

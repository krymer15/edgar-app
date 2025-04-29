# models/daily_index_metadata.py

from sqlalchemy import Column, Text, Date, TIMESTAMP, text
from models.base import Base

class DailyIndexMetadata(Base):
    __tablename__ = "daily_index_metadata"

    accession_number = Column(Text, primary_key=True)
    cik = Column(Text, nullable=False)
    form_type = Column(Text)
    filing_date = Column(Date)
    filing_url = Column(Text, nullable=False)

    downloaded = Column(Text, server_default=text("'false'"))

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

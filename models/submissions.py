from sqlalchemy import Column, Text, Date, ARRAY, Boolean, TIMESTAMP, ForeignKey
from models.base import Base

class SubmissionsMetadata(Base):
    __tablename__ = "submissions_metadata"

    accession_number = Column(Text, primary_key=True)
    cik = Column(Text, ForeignKey("companies_metadata.cik"), nullable=False)
    filing_date = Column(Date)
    report_date = Column(Date)
    form_type = Column(Text)
    items = Column(ARRAY(Text))
    primary_document = Column(Text)
    document_description = Column(Text)
    is_xbrl = Column(Boolean)
    is_inline_xbrl = Column(Boolean)
    acceptance_datetime = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP(timezone=True), server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP(timezone=True), server_default="CURRENT_TIMESTAMP")

# models/form4_filing.py

import uuid
from sqlalchemy import Column, String, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Form4Filing(Base):
    __tablename__ = "form4_filings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accession_number = Column(String, nullable=False, index=True)
    cik = Column(String, nullable=False, index=True)
    form_type = Column(String, nullable=False, default="4")
    filing_date = Column(Date, nullable=False)

    issuer = Column(JSON, nullable=True)  # JSON object with name + cik
    reporting_owners = Column(JSON, nullable=True)  # JSON object with name, role, etc.
    non_derivative_transactions = Column(JSON, nullable=True)  # List of JSON txns
    derivative_transactions = Column(JSON, nullable=True)  # List of JSON txns

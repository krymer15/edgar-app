from sqlalchemy import Column, String, Text, ARRAY, JSON, TIMESTAMP, text
from models.base import Base

class CompaniesMetadata(Base):
    __tablename__ = "companies_metadata"

    cik = Column(Text, primary_key=True)
    entity_type = Column(Text)
    sic = Column(Text)
    sic_description = Column(Text)
    name = Column(Text, nullable=False)
    tickers = Column(ARRAY(Text))
    exchanges = Column(ARRAY(Text))
    ein = Column(Text)
    description = Column(Text)
    website = Column(Text)
    investor_website = Column(Text)
    category = Column(Text)
    fiscal_year_end = Column(Text)
    state_of_incorporation = Column(Text)
    state_of_incorporation_description = Column(Text)
    mailing_address = Column(JSON)
    business_address = Column(JSON)
    phone = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


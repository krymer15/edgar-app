# models/index_record_model.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class IndexRecordModel(BaseModel):
    cik: str  # no length restriction
    form_type: str
    filing_date: date
    filing_url: str
    accession_number: str

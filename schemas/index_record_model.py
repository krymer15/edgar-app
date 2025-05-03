# models/index_record_model.py

from pydantic import BaseModel, Field
from typing import Optional


class IndexRecordModel(BaseModel):
    cik: str  # no length restriction
    form_type: str
    filing_date: str  # You can use date instead of str if validated
    filing_url: str
    accession_number: str

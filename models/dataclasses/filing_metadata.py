# models/dataclasses/filing_metadata.py
from dataclasses import dataclass
from datetime import date
from typing import Optional, bool

@dataclass
class FilingMetadata:
    accession_number: str
    cik: str
    form_type: str
    filing_date: date
    filing_url: Optional[str] = None
    issuer_cik: Optional[str] = None
    is_issuer: bool = True
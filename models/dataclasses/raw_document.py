# models/dataclasses/raw_document.py
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class RawDocument:
    accession_number: str
    cik: str
    form_type: str                # e.g., "8-K"
    document_type: str            # e.g. “sgml”, “index_html”, etc.
    filename: str
    source_url: str
    source_type: str              # usually same as document_type
    content: str                  # field for raw file body
    filing_date: date             
    description: Optional[str] = None
    is_primary: bool = False
    is_exhibit: bool = False
    is_data_support: bool = False
    accessible: bool = True
# models/dataclasses/raw_document.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class RawDocument:
    accession_number: str
    cik: str
    document_type: str            # e.g. “sgml”, “index_html”, etc.
    filename: str
    source_url: str
    source_type: str              # usually same as document_type
    description: Optional[str] = None
    is_primary: bool = False
    is_exhibit: bool = False
    is_data_support: bool = False
    accessible: bool = True
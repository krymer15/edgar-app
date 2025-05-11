# models/intermediate/parsed_document.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedDocument:
    cik: str
    accession_number: str
    form_type: str
    filename: str
    description: Optional[str]
    type: Optional[str]
    source_url: str
    source_type: str = "sgml"
    is_primary: bool = False
    is_exhibit: bool = False
    is_data_support: bool = False
    accessible: bool = True

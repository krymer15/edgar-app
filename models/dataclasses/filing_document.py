from dataclasses import dataclass
from typing import Optional

@dataclass
class FilingDocument:
    accession_number: str
    cik: str
    document_type: Optional[str]
    filename: Optional[str]
    description: Optional[str]
    source_url: Optional[str]
    source_type: Optional[str]
    is_primary: bool = False
    is_exhibit: bool = False
    is_data_support: bool = False
    accessible: bool = True

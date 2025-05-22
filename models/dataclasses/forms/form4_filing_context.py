# models/dataclasses/forms/form4_filing_context.py
from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Form4FilingContext:
    """
    Metadata container for Form 4 filing context.
    Used to pass filing metadata alongside XML content to the parser.
    """
    accession_number: str
    cik: str
    filing_date: Optional[date] = None
    form_type: str = "4"
    source_url: Optional[str] = None
    
    def __post_init__(self):
        """Set default filing date if not provided"""
        if self.filing_date is None:
            self.filing_date = datetime.now().date()
            
        # Ensure CIK is zero-padded to 10 digits if it's numeric
        if self.cik and self.cik.isdigit():
            self.cik = self.cik.zfill(10)
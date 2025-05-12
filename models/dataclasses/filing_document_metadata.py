# models/dataclasses/filing_document_metadata.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class FilingDocumentMetadata:
    """
    Pointer to a declared document within an SEC filing (e.g., exhibit or primary doc).
    This class holds metadata only — it does not include file content.
    """

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

    def __repr__(self):
        return (
            f"<FilingDocumentMetadata("
            f"cik={self.cik}, "
            f"accession={self.accession_number}, "
            f"filename={self.filename}, "
            f"type={self.type}, "
            f"primary={self.is_primary}, "
            f"exhibit={self.is_exhibit}, "
            f"accessible={self.accessible})>"
        )

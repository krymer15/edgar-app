# models/dataclasses/filing_document_record.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class FilingDocumentRecord:
    r'''
    The dataclass mirror of the ORM model, not a full document (e.g., no file content). Adding Record suffix clarifies it is a structured metadata entry.
    - Post-Adapter, ORM-Ready Format
    - Normalized, DB-ready metadata record (ORM-compatible)
    - Converted to → ORM model (FilingDocument) -- models\orm_models\filing_documents.py
    - Final Destination: Persistent → written to DB
    - Used by: FilingDocumentsCollector, FilingDocumentsWriter
    '''
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
    issuer_cik: Optional[str] = None  # New field

    def __repr__(self):
        return (
            f"<FilingDocumentRecord("
            f"cik={self.cik}, "
            f"accession={self.accession_number}, "
            f"filename={self.filename}, "
            f"doc_type={self.document_type}, "
            f"primary={self.is_primary}, "
            f"exhibit={self.is_exhibit}, "
            f"accessible={self.accessible}, "
            f"issuer_cik={self.issuer_cik or 'None'})>"
        )
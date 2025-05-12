# models/dataclasses/sgml_text_document.py

'''
Purpose: Carries the raw .txt content and basic metadata (CIK, accession) for downstream access in Pipeline 3 and better typed flow through parsing.

Use in:
- Return type of SgmlDownloader.download_sgml()
- Input to SgmlFilingParser.parse_to_documents()
'''
from dataclasses import dataclass
from typing import Optional

@dataclass
class SgmlTextDocument:
    cik: str
    accession_number: str
    content: str

    # Log/debug output
    def __repr__(self):
        return (
            f"<SgmlTextDocument("
            f"cik={self.cik}, "
            f"accession={self.accession_number}, "
            f"content_len={len(self.content)} chars)>"
        )

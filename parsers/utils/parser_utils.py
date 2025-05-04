# parsers/utils/parser_utils.py

from typing import Optional

def build_standard_output(
    parsed_type: str,
    source: str,
    content_type: str,
    accession_number: str,
    form_type: str,
    cik: str,
    filing_date: Optional[str],
    parsed_data: dict,
    metadata: Optional[dict] = None
) -> dict:
    return {
        "parsed_type": parsed_type,
        "source": source,
        "content_type": content_type,
        "accession_number": accession_number,
        "form_type": form_type,
        "cik": cik,
        "filing_date": filing_date,
        "metadata": metadata or {},
        "parsed_data": parsed_data,
    }

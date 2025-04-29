# utils/url_builder.py (repurposed from /downloaders/sec_downloader.py)

def normalize_cik(cik: str) -> str:
    """
    Pads CIK to 10 digits as required by SEC URLs.
    """
    return cik.zfill(10)

def construct_primary_document_url(cik: str, accession_number: str, primary_document: str) -> str:
    """
    Constructs a URL for accessing a primary document in EDGAR.
    """
    normalized_cik = normalize_cik(cik)
    accession_number_clean = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{normalized_cik}/{accession_number_clean}/{primary_document}"

def construct_submission_json_url(cik: str) -> str:
    """
    Constructs a URL for accessing the submissions JSON file for a company.
    """
    normalized_cik = normalize_cik(cik)
    return f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"

def construct_filing_index_url(cik: str, accession_number: str) -> str:
    """
    Constructs a URL to the filing index page (index.json or index.html).
    """
    normalized_cik = normalize_cik(cik)
    accession_number_clean = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{normalized_cik}/{accession_number_clean}/index.json"

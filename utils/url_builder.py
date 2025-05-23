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

def construct_sgml_txt_url(cik: str, accession_number: str) -> str:
    """
    Constructs the correct SGML .txt URL for a given CIK and accession number.
    Example output:
    https://www.sec.gov/Archives/edgar/data/1084869/000143774925013070/0001437749-25-013070.txt
    """
    normalized_cik = normalize_cik(cik)
    accession_clean = accession_number.replace("-", "")
    accession_dashed = f"{accession_clean[:10]}-{accession_clean[10:12]}-{accession_clean[12:]}"
    return f"https://www.sec.gov/Archives/edgar/data/{normalized_cik}/{accession_clean}/{accession_dashed}.txt"

def clean_accession_number(accession_number: str) -> str:
    # Returns the accession number with dashes removed, suitable for SEC URLs or filenames.    
    return accession_number.strip().replace("-", "")
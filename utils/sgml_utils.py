# utils/sgml_utils.py
import requests
from utils.url_builder import construct_sgml_txt_url

def download_sgml_for_accession(cik: str, accession_number: str, user_agent: str) -> str:
    """
    Download SGML submission content for a given accession number.
    
    Args:
        cik: Central Index Key
        accession_number: Accession number
        user_agent: User agent string for SEC API
        
    Returns:
        str: The raw SGML content
    """
    url = construct_sgml_txt_url(cik, accession_number.replace('-', ''))
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_issuer_cik_from_sgml(sgml_content: str) -> str:
    """
    Extract the issuer CIK from SGML content.
    For Form 4/3/5, 13D/G, etc. that have both issuer and reporting owners.
    
    Args:
        sgml_content: Raw SGML content
        
    Returns:
        str: The issuer CIK or empty string if not found
    """
    issuer_section_start = sgml_content.find("<ISSUER>")
    if issuer_section_start == -1:
        return ""
        
    issuer_section_end = sgml_content.find("</ISSUER>", issuer_section_start)
    if issuer_section_end == -1:
        issuer_section_end = sgml_content.find("<REPORTING-OWNER>", issuer_section_start)
    
    if issuer_section_end == -1:
        return ""
    
    issuer_section = sgml_content[issuer_section_start:issuer_section_end]
    
    cik_start = issuer_section.find("CENTRAL INDEX KEY:")
    if cik_start != -1:
        cik_line_end = issuer_section.find("\n", cik_start)
        if cik_line_end != -1:
            cik_line = issuer_section[cik_start:cik_line_end]
            cik = ''.join(c for c in cik_line if c.isdigit())
            return cik
    
    return ""
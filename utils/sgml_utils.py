# utils/sgml_utils.py
from utils.report_logger import log_warn, log_error
from utils.url_builder import construct_sgml_txt_url
from downloaders.sgml_downloader import SgmlDownloader

# Module-level instance
_shared_downloader = None

def get_shared_downloader(user_agent: str, request_delay_seconds: float = 0.1) -> SgmlDownloader:
    """
    Get or create a shared SgmlDownloader instance.
    
    Args:
        user_agent: User agent string for SEC API
        request_delay_seconds: Delay between requests in seconds
        
    Returns:
        SgmlDownloader instance
    """
    global _shared_downloader
    if _shared_downloader is None:
        _shared_downloader = SgmlDownloader(
            user_agent=user_agent, 
            request_delay_seconds=request_delay_seconds,
            use_cache=False  # Default to no file caching for utils module
        )
    return _shared_downloader

def download_sgml_for_accession(cik: str, accession_number: str, user_agent: str) -> str:
    """
    Download SGML submission content for a given accession number.
    Uses SgmlDownloader for proper rate limiting and caching.
    
    Args:
        cik: Central Index Key
        accession_number: Accession number
        user_agent: User agent string for SEC API
        
    Returns:
        str: The raw SGML content
    """
    # Input validation
    if not cik or not cik.strip():
        raise ValueError("CIK must be provided")
    if not accession_number or not accession_number.strip():
        raise ValueError("Accession number must be provided")
    if not user_agent or not user_agent.strip():
        raise ValueError("User agent must be provided")
    
    # Use the shared downloader
    try:
        downloader = get_shared_downloader(user_agent)
        url = construct_sgml_txt_url(cik, accession_number.replace('-', ''))
        return downloader.download(url)
    except Exception as e:
        log_error(f"Error downloading SGML for {cik}/{accession_number}: {str(e)}")
        raise

def extract_issuer_cik_from_sgml(sgml_content: str) -> str:
    """
    Extract the issuer CIK from SGML content.
    For Form 4/3/5, 13D/G, etc. that have both issuer and reporting owners.
    
    Args:
        sgml_content: Raw SGML content
        
    Returns:
        str: The issuer CIK or empty string if not found
    """
    if not sgml_content:
        log_warn("Empty SGML content provided to extract_issuer_cik_from_sgml")
        return ""
        
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
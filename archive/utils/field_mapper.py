# utils/field_mapper.py
### DEPRECATED

"""
Field mapping utilities to bridge inconsistencies between different modules,
especially for standardized handoffs at orchestration boundaries.

USE WITH ORCHESTRATORS!

# ⚠️ ACCESSION_CLEAN USAGE POLICY (derived field)
# `accession_clean` must ONLY be used locally (e.g., filenames or SEC URLs).
# Never add it to parsed metadata, writer input, or DB rows unless explicitly required.

"""

def get_accession_full(meta: dict) -> str:
    """
    Maps raw parsed filing metadata to a normalized accession_full string.
    Used for constructing filenames, SEC URLs, or orchestrator calls.

    Args:
        meta (dict): Dictionary containing at minimum 'accession_number'.

    Returns:
        str: Normalized accession_full (same as accession_number, trimmed).
    """
    return meta.get("accession_number", "").strip()


def get_cik(meta: dict) -> str:
    """
    Extracts and standardizes CIK from parsed filing metadata.
    Ensures no whitespace.

    Args:
        meta (dict): Dictionary containing at minimum 'cik'.

    Returns:
        str: CIK value as a string.
    """
    return meta.get("cik", "").strip()


def get_form_type(meta: dict) -> str:
    """
    Extracts and trims form type from parsed filing metadata.

    Args:
        meta (dict): Dictionary containing 'form_type'

    Returns:
        str: Filing form type (e.g., '8-K', '10-Q')
    """
    return meta.get("form_type", "").strip()


def get_filing_date(meta: dict) -> str:
    """
    Extracts the filing date in YYYY-MM-DD format from metadata.

    Args:
        meta (dict): Dictionary containing 'filing_date'

    Returns:
        str: Filing date as string
    """
    return str(meta.get("filing_date", "")).strip()

def get_accession_clean(meta: dict) -> str:
    """
    Returns the accession number with dashes removed, suitable for SEC URLs or filenames.
    
    Args:
        meta (dict): Dictionary with 'accession_number'

    Returns:
        str: Dashless accession number string
    """
    accession = meta.get("accession_number", "").strip()
    return accession.replace("-", "")

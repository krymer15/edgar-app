# utils/accession_formatter.py

"""
Utility for standardizing accession number formatting across the application.
This ensures consistency between database references, file names, and API calls.
"""

def format_for_db(accession_number: str) -> str:
    """
    Format an accession number for database storage.
    Database uses the standard format with dashes (0001234567-23-123456).
    
    Args:
        accession_number: Input accession number in any format
        
    Returns:
        Accession number with dashes for database storage
    """
    # Clean up any whitespace
    acc = accession_number.strip()
    
    # If it already has dashes, return as is (assuming proper format)
    if '-' in acc:
        return acc
    
    # If no dashes, insert them at standard positions (10 and 13)
    if len(acc) >= 18:
        return f"{acc[:10]}-{acc[10:12]}-{acc[12:]}"
    
    # If we can't format properly, return as is
    return acc


def format_for_url(accession_number: str) -> str:
    """
    Format an accession number for SEC URLs.
    SEC URLs require the accession number without dashes.
    
    Args:
        accession_number: Input accession number in any format
        
    Returns:
        Accession number without dashes for SEC URLs
    """
    # Clean up any whitespace and remove dashes
    return accession_number.strip().replace('-', '')


def format_for_filename(accession_number: str) -> str:
    """
    Format an accession number for filenames.
    Filenames typically use the accession number without dashes.
    
    Args:
        accession_number: Input accession number in any format
        
    Returns:
        Accession number without dashes for filenames
    """
    # Clean up any whitespace and remove dashes
    return accession_number.strip().replace('-', '')
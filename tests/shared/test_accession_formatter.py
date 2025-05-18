# tests/shared/test_accession_formatter.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.accession_formatter import format_for_db, format_for_url, format_for_filename

def test_format_for_db():
    """Test accession number formatting for database storage."""
    # Already has dashes
    assert format_for_db("0001234567-23-123456") == "0001234567-23-123456"
    
    # No dashes
    assert format_for_db("000123456723123456") == "0001234567-23-123456"
    
    # With whitespace
    assert format_for_db(" 0001234567-23-123456 ") == "0001234567-23-123456"
    
    # Short format (should return as is)
    assert format_for_db("123456") == "123456"
    
def test_format_for_url():
    """Test accession number formatting for SEC URLs."""
    # Already without dashes
    assert format_for_url("000123456723123456") == "000123456723123456"
    
    # With dashes
    assert format_for_url("0001234567-23-123456") == "000123456723123456"
    
    # With whitespace
    assert format_for_url(" 0001234567-23-123456 ") == "000123456723123456"

def test_format_for_filename():
    """Test accession number formatting for filenames."""
    # Should be same as URL format in this implementation
    assert format_for_filename("0001234567-23-123456") == "000123456723123456"
    assert format_for_filename(" 000123456723123456 ") == "000123456723123456"

if __name__ == "__main__":
    print("Running accession_formatter tests...")
    test_format_for_db()
    test_format_for_url()
    test_format_for_filename()
    print("All tests passed!")
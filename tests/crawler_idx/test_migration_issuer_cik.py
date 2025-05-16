# tests/crawler_idx/test_migration_issuer_cik.py

import os, sys
import pytest
from unittest.mock import patch, MagicMock
import re

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

def test_issuer_cik_migration_script_syntax():
    """Test that the migration script for adding issuer_cik is valid SQL."""
    # Path to the migration script
    script_path = os.path.join(
        os.path.dirname(__file__), 
        os.pardir, 
        os.pardir, 
        "sql", 
        "migrations", 
        "add_issuer_cik_to_filing_documents.sql"
    )
    
    # Verify the script exists
    assert os.path.exists(script_path), f"Migration script not found at {script_path}"
    
    # Read the script content
    with open(script_path, "r") as f:
        script_content = f.read()
    
    # Check for key SQL statements
    assert "ALTER TABLE filing_documents" in script_content
    assert "ADD COLUMN issuer_cik TEXT" in script_content
    assert "CREATE INDEX" in script_content
    assert "idx_filing_documents_issuer_cik" in script_content
    
    # Verify the script has a transaction
    assert re.search(r"BEGIN\s*;", script_content, re.IGNORECASE)
    assert re.search(r"COMMIT\s*;", script_content, re.IGNORECASE)
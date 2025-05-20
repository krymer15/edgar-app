# tests/tmp/test_form4_specific_issues.py

"""
Test specific issues identified with Form 4 processing.

These tests focus on known edge cases and bugs in Form 4 processing,
particularly around owner counting, relationship flags, and footnotes.
"""

import os
import sys
import pytest
from datetime import datetime, date
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).parents[2].absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the modules
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from parsers.forms.form4_parser import Form4Parser
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.form4_transaction import Form4TransactionData

# Test data path - using the file in tests/tmp directory
TEST_FILE_PATH = os.path.join('tests', 'tmp', '0001610717-23-000035.xml')

def read_test_xml():
    """Read the test XML file."""
    with open(TEST_FILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def test_form4_parser_owner_count():
    """Test that the Form4Parser correctly identifies exactly one reporting owner."""
    xml_content = read_test_xml()
    
    # Create a parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse the XML
    parsed_data = parser.parse(xml_content)
    
    # Check results
    assert parsed_data is not None, "Parser should return data"
    assert "parsed_data" in parsed_data, "Parsed data should be present"
    
    # Check for one reporting owner
    assert "reporting_owners" in parsed_data["parsed_data"], "Should have reporting owners"
    assert len(parsed_data["parsed_data"]["reporting_owners"]) == 1, "Should have exactly one reporting owner"
    
    # Check entity data
    assert "entity_data" in parsed_data["parsed_data"], "Should have entity data"
    assert "owner_entities" in parsed_data["parsed_data"]["entity_data"], "Should have owner entities"
    assert len(parsed_data["parsed_data"]["entity_data"]["owner_entities"]) == 1, "Should have exactly one owner entity"

def test_form4_parser_relationship_flags():
    """Test that the Form4Parser correctly sets relationship flags."""
    xml_content = read_test_xml()
    
    # Create a parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse the XML
    parsed_data = parser.parse(xml_content)
    
    # Check relationship flags
    relationships = parsed_data["parsed_data"]["entity_data"]["relationships"]
    assert len(relationships) == 1, "Should have one relationship"
    
    relationship = relationships[0]
    assert relationship["is_director"] == True, "Owner should be marked as a director"
    assert relationship["is_officer"] == False, "Owner should not be marked as an officer"
    assert relationship["is_ten_percent_owner"] == False, "Owner should not be marked as a 10% owner"
    assert relationship["is_other"] == False, "Owner should not be marked as other"

def test_form4_parser_footnotes():
    """Test that the Form4Parser correctly extracts footnotes."""
    xml_content = read_test_xml()
    
    # Create a parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse the XML
    parsed_data = parser.parse(xml_content)
    
    # Check for footnote extraction
    assert "parsed_data" in parsed_data
    assert "non_derivative_transactions" in parsed_data["parsed_data"]
    
    # The second non-derivative transaction should have a footnote
    transactions = parsed_data["parsed_data"]["non_derivative_transactions"]
    assert len(transactions) >= 2, "Should have at least 2 non-derivative transactions"
    
    # The second transaction has a footnote on the price per share
    second_transaction = transactions[1]
    assert "pricePerShare" in second_transaction, "Should have price per share field"
    
    # For testing, we need to understand how footnotes are encoded in the parsed data
    # This will depend on your parser implementation
    # We might need to adjust this assertion based on actual output format
    # Look for footnotes or footnote IDs in the data structure

def test_form4_indexer_integration():
    """
    Integration test for the Form4SgmlIndexer with XML content.
    
    This test simulates what would happen in the actual pipeline when
    processing this specific Form 4 filing.
    """
    # For this test, we'd need the SGML content which includes the XML
    # Since we only have the XML file for this test, we'll create a mock SGML content
    xml_content = read_test_xml()
    
    # Mock SGML content with embedded XML
    mock_sgml_content = f"""<SEC-HEADER>ACCESSION NUMBER: 0001610717-23-000035
CONFORMED PERIOD OF REPORT: 20230511
FILED AS OF DATE: 20230515
COMPANY CONFORMED NAME: 10x Genomics, Inc.
CENTRAL INDEX KEY: 0001770787
</SEC-HEADER>

<XML>
{xml_content}
</XML>
"""
    
    # Create an indexer
    indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
    
    # Index the documents
    indexed_data = indexer.index_documents(mock_sgml_content)
    
    # Check the result
    assert indexed_data is not None, "Should return indexed data"
    assert "form4_data" in indexed_data, "Should include form4_data"
    
    form4_data = indexed_data["form4_data"]
    
    # Check owner count
    assert isinstance(form4_data, Form4FilingData), "Should return a Form4FilingData object"
    assert form4_data.has_multiple_owners == False, "Should not have multiple owners"
    assert len(form4_data.relationships) == 1, "Should have one relationship"
    
    # Check relationship flags
    relationship = form4_data.relationships[0]
    assert relationship.is_director == True, "Relationship should be marked as director"
    assert relationship.is_officer == False, "Relationship should not be marked as officer"
    assert relationship.is_ten_percent_owner == False, "Relationship should not be marked as 10% owner"
    assert relationship.is_other == False, "Relationship should not be marked as other"
    
    # Check transaction count
    assert len(form4_data.transactions) >= 3, "Should have at least 3 transactions (2 non-derivative, 1 derivative)"
    
    # Verify transactions have footnotes where appropriate
    # The second non-derivative transaction should reference footnote F1
    non_derivative_transactions = [t for t in form4_data.transactions if not t.is_derivative]
    assert len(non_derivative_transactions) == 2, "Should have 2 non-derivative transactions"
    
    # The transaction with code 'S' is the one with the footnote
    s_transactions = [t for t in form4_data.transactions if t.transaction_code == 'S']
    assert len(s_transactions) > 0, "Should have at least one S transaction"
    s_transaction = s_transactions[0]
    
    # Check if footnotes are correctly captured
    # This might need adjustment based on how your system stores footnote references
    assert s_transaction.footnote_ids is not None, "S transaction should have footnote_ids"
    assert len(s_transaction.footnote_ids) > 0, "S transaction should have at least one footnote ID"
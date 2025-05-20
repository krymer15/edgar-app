# tests/forms/test_form4_footnote_extraction.py
"""
Tests for Bug 3 (footnote extraction) and Bug 5 (footnote ID transfer) fixes.

This test file validates:
1. Form4Parser correctly extracts footnote IDs from XML
2. Form4SgmlIndexer correctly transfers footnote IDs to Form4TransactionData objects
"""

import os
import pytest
from parsers.forms.form4_parser import Form4Parser
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from models.dataclasses.forms.form4_filing import Form4FilingData
from datetime import date

@pytest.fixture
def footnote_xml_content():
    """
    Loads a sample Form 4 XML file with footnotes from the fixtures directory.
    The file 0001610717-23-000035.xml contains footnotes with IDs F1 and F2.
    """
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             "fixtures", "0001610717-23-000035.xml")
    with open(test_path, "r", encoding="utf-8") as f:
        return f.read()

def test_form4_parser_extracts_footnotes(footnote_xml_content):
    """
    Test for Bug 3 fix: Validates Form4Parser.extract_*_transactions methods
    correctly extract footnote IDs from XML.
    """
    # Initialize parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse the XML content
    parsed_result = parser.parse(footnote_xml_content)
    
    # Check if parsing succeeded
    assert "error" not in parsed_result, f"Parser error: {parsed_result.get('error')}"
    
    # Extract the parsed data
    parsed_data = parsed_result.get("parsed_data", {})
    
    # Check non-derivative transactions for footnotes
    non_derivative_transactions = parsed_data.get("non_derivative_transactions", [])
    assert len(non_derivative_transactions) > 0, "No non-derivative transactions found"
    
    # The second non-derivative transaction has a footnote with ID F1
    second_transaction = non_derivative_transactions[1] if len(non_derivative_transactions) > 1 else None
    assert second_transaction is not None, "Second non-derivative transaction not found"
    assert "footnoteIds" in second_transaction, "footnoteIds field missing in transaction"
    assert second_transaction["footnoteIds"] is not None, "footnoteIds is None"
    assert "F1" in second_transaction["footnoteIds"], "Footnote ID F1 not found in non-derivative transaction"
    
    # Check derivative transactions for footnotes
    derivative_transactions = parsed_data.get("derivative_transactions", [])
    assert len(derivative_transactions) > 0, "No derivative transactions found"
    
    # The derivative transaction has a footnote with ID F2
    first_derivative = derivative_transactions[0]
    assert "footnoteIds" in first_derivative, "footnoteIds field missing in derivative transaction"
    assert first_derivative["footnoteIds"] is not None, "footnoteIds is None"
    assert "F2" in first_derivative["footnoteIds"], "Footnote ID F2 not found in derivative transaction"

def test_form4_sgml_indexer_transfers_footnote_ids(footnote_xml_content):
    """
    Test for Bug 5 fix: Validates Form4SgmlIndexer._add_transactions_from_parsed_xml 
    correctly transfers footnote IDs to Form4TransactionData objects.
    """
    # Parse the XML first using Form4Parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    parsed_result = parser.parse(footnote_xml_content)
    
    # Get the parsed transaction data
    parsed_data = parsed_result.get("parsed_data", {})
    non_derivative_transactions = parsed_data.get("non_derivative_transactions", [])
    derivative_transactions = parsed_data.get("derivative_transactions", [])
    
    # Create a Form4FilingData object to receive the transactions
    form4_data = Form4FilingData(
        accession_number="0001610717-23-000035",
        period_of_report=date(2023, 5, 11)
    )
    
    # Use the indexer's method to add transactions from parsed XML
    indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
    indexer._add_transactions_from_parsed_xml(form4_data, non_derivative_transactions, derivative_transactions)
    
    # Verify transactions were added
    assert len(form4_data.transactions) == len(non_derivative_transactions) + len(derivative_transactions)
    
    # Find the transactions with footnotes
    class_a_transaction = next((t for t in form4_data.transactions 
                               if t.security_title == "Class A Common Stock" 
                               and t.transaction_code == "S"), None)
    assert class_a_transaction is not None, "Class A Common Stock sale transaction not found"
    assert class_a_transaction.footnote_ids, "footnote_ids missing or empty in Class A transaction"
    assert "F1" in class_a_transaction.footnote_ids, "Footnote ID F1 not transferred to Class A transaction"
    
    option_transaction = next((t for t in form4_data.transactions 
                              if t.security_title == "Stock Option (right to buy)"), None)
    assert option_transaction is not None, "Stock Option transaction not found"
    assert option_transaction.footnote_ids, "footnote_ids missing or empty in Stock Option transaction"
    assert "F2" in option_transaction.footnote_ids, "Footnote ID F2 not transferred to Stock Option transaction"

if __name__ == "__main__":
    # When run directly, execute both tests
    test_xml = footnote_xml_content()
    
    print("Testing Form4Parser footnote extraction...")
    test_form4_parser_extracts_footnotes(test_xml)
    print("✅ Form4Parser footnote extraction test passed")
    
    print("Testing Form4SgmlIndexer footnote ID transfer...")
    test_form4_sgml_indexer_transfers_footnote_ids(test_xml)
    print("✅ Form4SgmlIndexer footnote ID transfer test passed")
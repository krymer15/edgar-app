# tests/tmp/debug_form4_processing.py

"""
Debugging script for Form 4 processing.

This script isolates each component of the Form 4 processing pipeline
to identify issues with a specific Form 4 filing.
"""

import os
import sys
from datetime import datetime

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from parsers.forms.form4_parser import Form4Parser

# Test file path
TEST_FILE_PATH = os.path.join('tests', 'tmp', '0001610717-23-000035.xml')

def read_test_xml():
    """Read the test XML file"""
    with open(TEST_FILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def debug_form4_parser():
    """Debug the Form4Parser directly with XML content"""
    print("\n=== Testing Form4Parser with XML ===")
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
    print(f"Parsed data: {'Success' if parsed_data else 'Failed'}")
    if parsed_data:
        # Check reporting owners 
        reporting_owners = parsed_data["parsed_data"]["reporting_owners"]
        print(f"Number of reporting owners: {len(reporting_owners)}")
        for i, owner in enumerate(reporting_owners):
            print(f"  Owner {i+1}: {owner['name']} (CIK: {owner['cik']})")
        
        # Check entity data
        entity_data = parsed_data["parsed_data"]["entity_data"]
        owner_entities = entity_data.get("owner_entities", [])
        print(f"Number of owner entities: {len(owner_entities)}")
        
        # Check relationships
        relationships = entity_data.get("relationships", [])
        print(f"Number of relationships: {len(relationships)}")
        for i, rel in enumerate(relationships):
            print(f"  Relationship {i+1}:")
            print(f"    is_director: {rel.get('is_director', False)}")
            print(f"    is_officer: {rel.get('is_officer', False)}")
            print(f"    is_ten_percent_owner: {rel.get('is_ten_percent_owner', False)}")
            print(f"    is_other: {rel.get('is_other', False)}")
        
        # Check transactions
        transactions = []
        if "non_derivative_transactions" in parsed_data["parsed_data"]:
            transactions.extend(parsed_data["parsed_data"]["non_derivative_transactions"])
        if "derivative_transactions" in parsed_data["parsed_data"]:
            transactions.extend(parsed_data["parsed_data"]["derivative_transactions"])
        
        print(f"Number of transactions: {len(transactions)}")
        for i, txn in enumerate(transactions):
            print(f"  Transaction {i+1}: {txn.get('securityTitle', 'Unknown')}")
            print(f"    Type: {'Derivative' if 'conversionOrExercisePrice' in txn else 'Non-derivative'}")
            print(f"    Code: {txn.get('transactionCode', 'Unknown')}")
            
            # Check for footnotes
            has_footnote = False
            for key, value in txn.items():
                if isinstance(value, dict) and 'footnoteId' in value:
                    has_footnote = True
                    print(f"    Footnote found on field: {key}")
            
            if not has_footnote:
                for key, value in txn.items():
                    if key == 'footnoteId' or (isinstance(value, dict) and 'footnoteId' in value):
                        has_footnote = True
                        print(f"    Footnote found on field: {key}")
            
            print(f"    Has footnote: {has_footnote}")

def debug_form4_indexer():
    """Debug the Form4SgmlIndexer with simulated SGML content"""
    print("\n=== Testing Form4SgmlIndexer with simulated SGML ===")
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
    
    # Check results
    print(f"Indexed data: {'Success' if indexed_data else 'Failed'}")
    if indexed_data and "form4_data" in indexed_data:
        form4_data = indexed_data["form4_data"]
        
        # Check owner count and multiple owners flag
        print(f"Has multiple owners flag: {form4_data.has_multiple_owners}")
        print(f"Number of relationships: {len(form4_data.relationships)}")
        
        # Check relationships
        for i, rel in enumerate(form4_data.relationships):
            print(f"  Relationship {i+1}:")
            print(f"    is_director: {rel.is_director}")
            print(f"    is_officer: {rel.is_officer}")
            print(f"    is_ten_percent_owner: {rel.is_ten_percent_owner}")
            print(f"    is_other: {rel.is_other}")
            print(f"    Relationship type: {rel.relationship_type}")
        
        # Check transactions
        print(f"Number of transactions: {len(form4_data.transactions)}")
        for i, txn in enumerate(form4_data.transactions):
            print(f"  Transaction {i+1}: {txn.security_title}")
            print(f"    Type: {'Derivative' if txn.is_derivative else 'Non-derivative'}")
            print(f"    Code: {txn.transaction_code}")
            print(f"    Footnote IDs: {txn.footnote_ids}")

def main():
    print("=== Form 4 Processing Debug Script ===")
    print(f"Test file: {TEST_FILE_PATH}")
    
    if not os.path.exists(TEST_FILE_PATH):
        print(f"ERROR: Test file not found at {TEST_FILE_PATH}")
        sys.exit(1)
    
    # Run each debugging function
    debug_form4_parser()
    debug_form4_indexer()
    
    print("\nDebugging complete.")

if __name__ == "__main__":
    main()
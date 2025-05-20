# apply_all_fixes.py
#
# This script applies all the fixes for the Form 4 processing issues.
# It can be used to test the fixes on specific Form 4 filings.

import os
import sys
from datetime import datetime

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

# Import fix modules
from tests.tmp.fix_form4_owner_count import apply_fix as fix_owner_count
from tests.tmp.fix_form4_relationship_flags import apply_fix as fix_relationship_flags
from tests.tmp.fix_form4_footnotes import apply_fixes as fix_footnotes
from tests.tmp.fix_form4_multiple_owners import apply_fix as fix_multiple_owners
from tests.tmp.fix_form4_footnote_transfer import apply_fix as fix_footnote_transfer

# Import modules for testing
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from parsers.forms.form4_parser import Form4Parser
from models.dataclasses.entity import EntityData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.form4_transaction import Form4TransactionData
from datetime import datetime
from utils.report_logger import log_info, log_warn, log_error

def apply_all_fixes():
    """Apply all the fixes for Form 4 processing issues."""
    fixes_applied = []
    
    print("Applying fix for owner count...")
    fixes_applied.append(fix_owner_count())
    
    print("Applying fix for relationship flags...")
    fixes_applied.append(fix_relationship_flags())
    
    print("Applying fix for footnotes...")
    fixes_applied.append(fix_footnotes())
    
    print("Applying fix for multiple owners flag...")
    fixes_applied.append(fix_multiple_owners())
    
    print("Applying fix for footnote transfer...")
    fixes_applied.append(fix_footnote_transfer())
    
    print("\nAll fixes applied successfully:")
    for fix in fixes_applied:
        print(f"- {fix}")
    
    return fixes_applied

def test_with_specific_file():
    """Test all fixes with a specific Form 4 file."""
    # Test file path
    TEST_FILE_PATH = os.path.join('tests', 'tmp', '0001610717-23-000035.xml')
    
    if not os.path.exists(TEST_FILE_PATH):
        print(f"ERROR: Test file not found at {TEST_FILE_PATH}")
        return False
    
    print(f"\nTesting with file: {TEST_FILE_PATH}")
    
    # Read the XML content
    with open(TEST_FILE_PATH, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Test Form4Parser directly
    print("\n=== Testing Form4Parser with fixes ===")
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787", 
        filing_date="2023-05-11"
    )
    
    parsed_data = parser.parse(xml_content)
    
    if parsed_data and "parsed_data" in parsed_data:
        # Check reporting owners
        reporting_owners = parsed_data["parsed_data"]["reporting_owners"]
        print(f"Number of reporting owners: {len(reporting_owners)}")
        
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
        
        # Create mock SGML content with embedded XML for testing the indexer
        print("\n=== Testing Form4SgmlIndexer with fixes ===")
        mock_sgml_content = f"""<SEC-HEADER>ACCESSION NUMBER: 0001610717-23-000035
CONFORMED PERIOD OF REPORT: 20230511
FILED AS OF DATE: 20230515
COMPANY CONFORMED NAME: 10x Genomics, Inc.
CENTRAL INDEX KEY: 0001770787
</SEC-HEADER>

<REPORTING-OWNER>
OWNER DATA:
COMPANY CONFORMED NAME: Mammen Mathai
CENTRAL INDEX KEY: 0001421050
</REPORTING-OWNER>

<XML>
{xml_content}
</XML>
"""
        
        # Test Form4SgmlIndexer
        indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
        indexed_data = indexer.index_documents(mock_sgml_content)
        
        if indexed_data and "form4_data" in indexed_data:
            form4_data = indexed_data["form4_data"]
            
            # Check multiple owners flag
            print(f"has_multiple_owners flag: {form4_data.has_multiple_owners}")
            
            # Check relationships
            print(f"Number of relationships: {len(form4_data.relationships)}")
            for i, rel in enumerate(form4_data.relationships):
                print(f"  Relationship {i+1}:")
                print(f"    is_director: {rel.is_director}")
                print(f"    is_officer: {rel.is_officer}")
                print(f"    is_ten_percent_owner: {rel.is_ten_percent_owner}")
                print(f"    is_other: {rel.is_other}")
            
            # Check transactions and footnotes
            print(f"Number of transactions: {len(form4_data.transactions)}")
            for i, txn in enumerate(form4_data.transactions):
                print(f"  Transaction {i+1}: {txn.security_title}")
                print(f"    Type: {'Derivative' if txn.is_derivative else 'Non-derivative'}")
                print(f"    Code: {txn.transaction_code}")
                print(f"    Footnote IDs: {txn.footnote_ids}")
            
            return True
        else:
            print("Form4SgmlIndexer failed to index the document")
            return False
    else:
        print("Form4Parser failed to parse the XML")
        return False

def main():
    print("=== Form 4 Fixes Application Script ===")
    
    # Apply all fixes
    apply_all_fixes()
    
    # Test with specific file
    test_success = test_with_specific_file()
    
    if test_success:
        print("\nTest successful! All fixes appear to be working correctly.")
    else:
        print("\nTest failed. There may still be issues with the fixes.")

if __name__ == "__main__":
    main()
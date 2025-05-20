#!/usr/bin/env python
# tests/tmp/test_bug2_fix.py

"""
Test script to verify that the fix for Bug 2 (relationship flags) works properly.
This script tests the handling of "true" values in relationship flags.
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from lxml import etree
import io

# Add project root to sys.path
project_root = str(Path(__file__).parents[2].absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from parsers.forms.form4_parser import Form4Parser
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer

def test_form4_parser_with_true_value():
    """Test Form4Parser with 'true' values in relationship flags"""
    # The test XML file already has <isDirector>true</isDirector>
    test_file_path = os.path.join('tests', 'tmp', '0001610717-23-000035.xml')
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
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
    print("Form4Parser results:")
    print(f"  is_director: {relationship['is_director']}")
    print(f"  is_officer: {relationship['is_officer']}")
    print(f"  is_ten_percent_owner: {relationship['is_ten_percent_owner']}")
    print(f"  is_other: {relationship['is_other']}")
    
    # This should be True with our fix
    assert relationship["is_director"] == True, "Owner should be marked as a director"
    
    return True

def test_form4_sgml_indexer_with_true_value():
    """Test Form4SgmlIndexer with 'true' values in relationship flags"""
    # The test XML file already has <isDirector>true</isDirector>
    test_file_path = os.path.join('tests', 'tmp', '0001610717-23-000035.xml')
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Create mock SGML content with embedded XML
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
    
    # Create an indexer
    indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
    
    # Index the documents
    indexed_data = indexer.index_documents(mock_sgml_content)
    
    # Check the relationships
    form4_data = indexed_data["form4_data"]
    assert len(form4_data.relationships) == 1, "Should have one relationship"
    
    relationship = form4_data.relationships[0]
    print("\nForm4SgmlIndexer results:")
    print(f"  is_director: {relationship.is_director}")
    print(f"  is_officer: {relationship.is_officer}")
    print(f"  is_ten_percent_owner: {relationship.is_ten_percent_owner}")
    print(f"  is_other: {relationship.is_other}")
    
    # This should be True with our fix
    assert relationship.is_director == True, "Owner should be marked as a director"
    
    return True

if __name__ == "__main__":
    print("Testing Bug 2 Fix for Form4 Relationship Flags...")
    print("-" * 50)
    
    parser_result = test_form4_parser_with_true_value()
    indexer_result = test_form4_sgml_indexer_with_true_value()
    
    print("-" * 50)
    if parser_result and indexer_result:
        print("SUCCESS: Bug 2 (Relationship Flags) has been fixed!")
    else:
        print("FAILED: The fix for Bug 2 (Relationship Flags) is not working correctly.")
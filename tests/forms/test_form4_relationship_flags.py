#!/usr/bin/env python
# tests/forms/test_form4_relationship_flags.py

"""
Test that Form4Parser and Form4SgmlIndexer correctly parse relationship flags
regardless of whether they're represented as "1" or "true" in the XML.
"""

from dev_tools.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

import os
import pytest
from parsers.forms.form4_parser import Form4Parser
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer

def load_fixture(filename):
    """
    Loads a sample Form 4 XML file from the fixtures directory.
    """
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures", filename)
    with open(test_path, "r", encoding="utf-8") as f:
        return f.read()

def test_form4_parser_relationship_flags_true():
    """
    Test that Form4Parser correctly parses 'true' relationship flag values.
    """
    xml_content = load_fixture("0001610717-23-000035.xml")  # Uses 'true' for isDirector

    # Create parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse XML
    result = parser.parse(xml_content)
    
    # Check result structure
    assert "error" not in result, f"Parser error: {result.get('error', 'Unknown error')}"
    assert "parsed_data" in result, "Missing parsed_data in result"
    
    # Check relationship flags
    parsed_data = result["parsed_data"]
    assert "entity_data" in parsed_data, "Missing entity_data in parsed_data"
    entity_data = parsed_data["entity_data"]
    
    # Check for relationships
    assert "relationships" in entity_data, "Missing relationships in entity_data"
    relationships = entity_data["relationships"]
    assert len(relationships) == 1, f"Expected 1 relationship, got {len(relationships)}"
    
    # Check relationship flags
    relationship = relationships[0]
    assert relationship["is_director"] is True, "isDirector='true' was not correctly parsed as True"

def test_form4_parser_relationship_flags_numeric():
    """
    Test that Form4Parser correctly parses '1' relationship flag values.
    """
    xml_content = load_fixture("0001610717-23-000035_rel_num.xml")  # Uses '1' for isDirector

    # Create parser
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse XML
    result = parser.parse(xml_content)
    
    # Check result structure
    assert "error" not in result, f"Parser error: {result.get('error', 'Unknown error')}"
    assert "parsed_data" in result, "Missing parsed_data in result"
    
    # Check relationship flags
    parsed_data = result["parsed_data"]
    assert "entity_data" in parsed_data, "Missing entity_data in parsed_data"
    entity_data = parsed_data["entity_data"]
    
    # Check for relationships
    assert "relationships" in entity_data, "Missing relationships in entity_data"
    relationships = entity_data["relationships"]
    assert len(relationships) == 1, f"Expected 1 relationship, got {len(relationships)}"
    
    # Check relationship flags
    relationship = relationships[0]
    assert relationship["is_director"] is True, "isDirector='1' was not correctly parsed as True"

def test_sgml_indexer_relationship_flags_true():
    """
    Test that Form4SgmlIndexer correctly parses 'true' relationship flag values.
    """
    xml_content = load_fixture("0001610717-23-000035.xml")  # Uses 'true' for isDirector
    
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
    
    # Create indexer
    indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
    
    # Process the SGML
    result = indexer.index_documents(mock_sgml_content)
    
    # Check result structure
    assert "form4_data" in result, "Missing form4_data in result"
    form4_data = result["form4_data"]
    
    # Check relationships
    assert len(form4_data.relationships) == 1, f"Expected 1 relationship, got {len(form4_data.relationships)}"
    
    # Check relationship flags
    relationship = form4_data.relationships[0]
    assert relationship.is_director is True, "isDirector='true' was not correctly parsed as True by SGML indexer"

def test_sgml_indexer_relationship_flags_numeric():
    """
    Test that Form4SgmlIndexer correctly parses '1' relationship flag values.
    """
    xml_content = load_fixture("0001610717-23-000035_rel_num.xml")  # Uses '1' for isDirector
    
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
    
    # Create indexer
    indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
    
    # Process the SGML
    result = indexer.index_documents(mock_sgml_content)
    
    # Check result structure
    assert "form4_data" in result, "Missing form4_data in result"
    form4_data = result["form4_data"]
    
    # Check relationships
    assert len(form4_data.relationships) == 1, f"Expected 1 relationship, got {len(form4_data.relationships)}"
    
    # Check relationship flags
    relationship = form4_data.relationships[0]
    assert relationship.is_director is True, "isDirector='1' was not correctly parsed as True by SGML indexer"

if __name__ == "__main__":
    test_form4_parser_relationship_flags_true()
    print("✅ test_form4_parser_relationship_flags_true passed.")
    
    test_form4_parser_relationship_flags_numeric()
    print("✅ test_form4_parser_relationship_flags_numeric passed.")
    
    test_sgml_indexer_relationship_flags_true()
    print("✅ test_sgml_indexer_relationship_flags_true passed.")
    
    test_sgml_indexer_relationship_flags_numeric()
    print("✅ test_sgml_indexer_relationship_flags_numeric passed.")
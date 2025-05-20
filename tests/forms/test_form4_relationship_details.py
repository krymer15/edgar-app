# tests/forms/test_form4_relationship_details.py
"""
Tests for Bug 6 fix: Relationship details field population in Form4RelationshipData objects.

This test verifies that the relationship_details field is properly populated with 
structured JSON metadata about issuer-owner relationships.
"""

import os
import pytest
from parsers.forms.form4_parser import Form4Parser
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from datetime import date

@pytest.fixture
def sample_xml_content():
    """Load the sample Form 4 XML with director relationship."""
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             "fixtures", "0001610717-23-000035.xml")
    with open(test_path, "r", encoding="utf-8") as f:
        return f.read()

def test_relationship_details_populated(sample_xml_content):
    """Test that relationship_details field is populated with structured JSON metadata."""
    # Create a parser to process the XML
    parser = Form4Parser(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date="2023-05-11"
    )
    
    # Parse the XML
    parsed_result = parser.parse(sample_xml_content)
    assert "error" not in parsed_result, f"Parser error: {parsed_result.get('error')}"
    
    # Extract entity data
    parsed_data = parsed_result.get("parsed_data", {})
    entity_data = parsed_data.get("entity_data", {})
    
    # Create Form4FilingData using Form4SgmlIndexer
    indexer = Form4SgmlIndexer(cik="0001770787", accession_number="0001610717-23-000035")
    form4_data = indexer.extract_form4_data("")  # Empty string as we're not using SGML
    
    # Apply the XML data to the Form4FilingData
    indexer._update_form4_data_from_xml(form4_data, entity_data)
    
    # Verify relationship_details is populated
    assert len(form4_data.relationships) > 0, "No relationships created"
    
    # Check relationship_details structure
    relationship = form4_data.relationships[0]
    assert relationship.relationship_details is not None, "relationship_details is None"
    
    # Verify required fields
    details = relationship.relationship_details
    assert "filing_date" in details, "filing_date missing from relationship_details"
    assert "accession_number" in details, "accession_number missing from relationship_details"
    assert "form_type" in details, "form_type missing from relationship_details"
    assert "issuer" in details, "issuer missing from relationship_details"
    assert "owner" in details, "owner missing from relationship_details"
    assert "roles" in details, "roles missing from relationship_details"
    
    # Check issuer and owner details
    assert "name" in details["issuer"], "issuer name missing"
    assert "cik" in details["issuer"], "issuer cik missing"
    assert "name" in details["owner"], "owner name missing"
    assert "cik" in details["owner"], "owner cik missing"
    assert "type" in details["owner"], "owner type missing"
    
    # Verify 10x Genomics specific data
    assert details["issuer"]["name"] == "10x Genomics, Inc.", "Wrong issuer name"
    assert details["issuer"]["cik"] == "1770787", "Wrong issuer CIK"
    assert details["owner"]["name"] == "Mammen Mathai", "Wrong owner name"
    assert details["owner"]["cik"] == "1421050", "Wrong owner CIK"
    assert details["owner"]["type"] == "person", "Wrong owner type"
    
    # For this particular fixture, verify director role is set
    assert "director" in details["roles"], "Director role not found"
    
    # Make sure the roles array contains the correct data based on XML
    role_types = set()
    for role in details["roles"]:
        if isinstance(role, str):
            role_types.add(role)
        elif isinstance(role, dict) and "type" in role:
            role_types.add(role["type"])
    
    # This specific XML has a director role
    assert "director" in role_types, "Director role missing from roles array"

def test_complex_relationship_details():
    """Test relationship_details with multiple roles and complex structure."""
    # Create a Form4SgmlIndexer instance
    indexer = Form4SgmlIndexer(cik="0000123456", accession_number="0000123456-23-000001")
    
    # Create mock data
    form4_data = indexer.extract_form4_data("")  # Empty string as we're not using SGML
    
    # Create mock entities and relationship data
    from models.dataclasses.entity import EntityData
    issuer_entity = EntityData(cik="123456", name="Test Company", entity_type="company")
    owner_entity = EntityData(cik="654321", name="John Smith", entity_type="person")
    
    relationship_data = {
        "is_director": True,
        "is_officer": True,
        "is_ten_percent_owner": True,
        "is_other": True,
        "officer_title": "CEO and President",
        "other_text": "Founder"
    }
    
    entity_data = {
        "issuer_entity": issuer_entity,
        "owner_entities": [owner_entity],
        "relationships": [relationship_data]
    }
    
    # Apply the mock data
    indexer._update_form4_data_from_xml(form4_data, entity_data)
    
    # Verify the relationship was created
    assert len(form4_data.relationships) == 1, "Relationship not created"
    
    # Check relationship_details
    relationship = form4_data.relationships[0]
    details = relationship.relationship_details
    
    # Check basic structure
    assert details["issuer"]["name"] == "Test Company"
    assert details["owner"]["name"] == "John Smith"
    
    # Check roles array - should have all 4 types
    role_types = set()
    officer_title = None
    other_description = None
    
    for role in details["roles"]:
        if isinstance(role, str):
            role_types.add(role)
        elif isinstance(role, dict) and "type" in role:
            role_types.add(role["type"])
            if role["type"] == "officer" and "title" in role:
                officer_title = role["title"]
            elif role["type"] == "other" and "description" in role:
                other_description = role["description"]
    
    assert "director" in role_types, "Director role missing"
    assert "officer" in role_types, "Officer role missing"
    assert "10_percent_owner" in role_types, "10 percent owner role missing"
    assert "other" in role_types, "Other role missing"
    
    # Check role details
    assert officer_title == "CEO and President", "Officer title not preserved"
    assert other_description == "Founder", "Other description not preserved"

if __name__ == "__main__":
    # When run directly, execute both tests
    print("Testing relationship_details population...")
    xml_content = sample_xml_content()
    test_relationship_details_populated(xml_content)
    print("✅ Basic relationship_details test passed")
    
    test_complex_relationship_details()
    print("✅ Complex relationship_details test passed")
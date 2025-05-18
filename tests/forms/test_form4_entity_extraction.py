# tests/forms/test_form4_entity_extraction.py

from dev_tools.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

import os
import pytest
from parsers.forms.form4_parser import Form4Parser
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from models.dataclasses.entity import EntityData

def load_fixture():
    """
    Loads a sample Form 4 XML file from the fixtures directory.
    """
    test_path = os.path.join(os.path.dirname(__file__), "fixtures", "form4_sample.xml")
    with open(test_path, "r", encoding="utf-8") as f:
        return f.read()

def test_entity_extraction_from_xml():
    """
    Test the enhanced entity extraction from Form 4 XML directly.
    """
    xml_content = load_fixture()
    
    # Test parameters
    accession_number = "0000000000-00-000000"
    cik = "0000000000"
    filing_date = "2025-01-01"
    
    # Parse using the enhanced Form4Parser
    parser = Form4Parser(
        accession_number=accession_number,
        cik=cik,
        filing_date=filing_date
    )
    result = parser.parse(xml_content)
    
    # Verify we got a valid result
    assert "error" not in result, f"Parser error: {result.get('error', 'Unknown error')}"
    assert "parsed_data" in result, "Missing parsed_data in result"
    
    # Verify entity data is present
    parsed_data = result["parsed_data"]
    assert "entity_data" in parsed_data, "Missing entity_data in parsed_data"
    entity_data = parsed_data["entity_data"]
    
    # Check issuer entity
    assert "issuer_entity" in entity_data, "Missing issuer_entity in entity_data"
    issuer_entity = entity_data["issuer_entity"]
    assert isinstance(issuer_entity, EntityData), "issuer_entity is not an EntityData object"
    # Strip leading zeros when comparing CIKs
    assert issuer_entity.cik.lstrip("0") == "1084869", f"Incorrect issuer CIK: {issuer_entity.cik}"
    assert issuer_entity.name == "1 800 FLOWERS COM INC", f"Incorrect issuer name: {issuer_entity.name}"
    assert issuer_entity.entity_type == "company", f"Incorrect issuer entity_type: {issuer_entity.entity_type}"
    
    # Check owner entities
    assert "owner_entities" in entity_data, "Missing owner_entities in entity_data"
    owner_entities = entity_data["owner_entities"]
    assert isinstance(owner_entities, list), "owner_entities is not a list"
    assert len(owner_entities) == 3, f"Expected 3 owner entities, got {len(owner_entities)}"
    
    # Check first owner entity
    first_owner = owner_entities[0]
    assert isinstance(first_owner, EntityData), "First owner is not an EntityData object"
    # Strip leading zeros when comparing CIKs
    assert first_owner.cik.lstrip("0") == "1959730", f"Incorrect first owner CIK: {first_owner.cik}"
    assert first_owner.name == "Fund 1 Investments, LLC", f"Incorrect first owner name: {first_owner.name}"
    assert first_owner.entity_type == "company", f"Incorrect first owner entity_type: {first_owner.entity_type}"
    
    # Check relationships
    assert "relationships" in entity_data, "Missing relationships in entity_data"
    relationships = entity_data["relationships"]
    assert isinstance(relationships, list), "relationships is not a list"
    assert len(relationships) == 3, f"Expected 3 relationships, got {len(relationships)}"
    
    # Check first relationship
    first_rel = relationships[0]
    assert "issuer_cik" in first_rel, "Missing issuer_cik in first relationship"
    assert "owner_cik" in first_rel, "Missing owner_cik in first relationship"
    # Strip leading zeros when comparing CIKs to handle format differences
    assert first_rel["issuer_cik"].lstrip("0") == "1084869", f"Incorrect issuer_cik in relationship: {first_rel['issuer_cik']}"
    assert first_rel["owner_cik"].lstrip("0") == "1959730", f"Incorrect owner_cik in relationship: {first_rel['owner_cik']}"
    assert first_rel["is_ten_percent_owner"] is True, "First relationship should be ten percent owner"

def test_form4_sgml_indexer_entity_attachment():
    """
    Test that Form4SgmlIndexer correctly attaches entity objects to Form4FilingData.
    """
    xml_content = load_fixture()
    
    # Create a mock SGML content that includes the XML
    mock_sgml = f"""<SEC-HEADER>
ACCESSION NUMBER:  0000000000-00-000000
CONFORMED SUBMISSION TYPE: 4
PUBLIC DOCUMENT COUNT: 1
FILED AS OF DATE: 20250101
</SEC-HEADER>

<XML>
{xml_content}
</XML>
"""

    # Create indexer and process the XML
    indexer = Form4SgmlIndexer(cik="0000000000", accession_number="0000000000-00-000000")
    result = indexer.index_documents(mock_sgml)
    
    # Verify form4_data object
    assert "form4_data" in result, "Missing form4_data in result"
    form4_data = result["form4_data"]
    
    # Verify entity attributes were attached directly to form4_data
    assert hasattr(form4_data, "issuer_entity"), "issuer_entity not attached to form4_data"
    assert hasattr(form4_data, "owner_entities"), "owner_entities not attached to form4_data"
    
    # Check issuer entity
    issuer_entity = form4_data.issuer_entity
    assert isinstance(issuer_entity, EntityData), "issuer_entity is not an EntityData object"
    # Strip leading zeros when comparing CIKs
    assert issuer_entity.cik.lstrip("0") == "1084869", f"Incorrect issuer CIK: {issuer_entity.cik}"
    
    # Check owner entities
    owner_entities = form4_data.owner_entities
    assert isinstance(owner_entities, list), "owner_entities is not a list"
    assert len(owner_entities) == 3, f"Expected 3 owner entities, got {len(owner_entities)}"
    
    # Check relationships
    assert len(form4_data.relationships) == 3, f"Expected 3 relationships, got {len(form4_data.relationships)}"
    
    # Check relationship IDs match entity IDs
    for idx, rel in enumerate(form4_data.relationships):
        assert rel.issuer_entity_id == form4_data.issuer_entity.id, f"Relationship {idx} issuer ID mismatch"
        assert rel.owner_entity_id == form4_data.owner_entities[idx].id, f"Relationship {idx} owner ID mismatch"

if __name__ == "__main__":
    test_entity_extraction_from_xml()
    print("✅ test_entity_extraction_from_xml passed.")
    
    test_form4_sgml_indexer_entity_attachment()
    print("✅ test_form4_sgml_indexer_entity_attachment passed.")
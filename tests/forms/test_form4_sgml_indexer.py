# tests/forms/test_form4_sgml_indexer.py
import pytest
from unittest.mock import patch, MagicMock
import os
from datetime import date
from uuid import UUID

from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer

@pytest.fixture
def sample_sgml_content():
    # Load sample Form 4 SGML content from fixture file
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),  # Go up one level from forms
        "fixtures",
        "0000921895-25-001190.txt"
    )

    # Fall back to embedded sample if file doesn't exist
    if not os.path.exists(fixture_path):
        # Create a minimal test fixture if file doesn't exist
        return """<SEC-HEADER>
ACCESSION NUMBER:             0001234567-25-000001
CONFORMED SUBMISSION TYPE:    4
CONFORMED PERIOD OF REPORT:   20250514
FILED AS OF DATE:             20250515

<ISSUER>
COMPANY DATA:
    COMPANY CONFORMED NAME:                   TEST ISSUER INC
    CENTRAL INDEX KEY:                                0001234567

<REPORTING-OWNER>
OWNER DATA:
    COMPANY CONFORMED NAME:                   TEST OWNER
    CENTRAL INDEX KEY:                                0009876543
</SEC-HEADER>

<DOCUMENT>
<TYPE>4
<SEQUENCE>1
<FILENAME>form4.xml
<TEXT>
<XML>
<?xml version="1.0"?>
<ownershipDocument>
<issuer>
    <issuerName>TEST ISSUER INC</issuerName>
    <issuerCik>0001234567</issuerCik>
</issuer>
<reportingOwner>
    <reportingOwnerId>
    <rptOwnerCik>0009876543</rptOwnerCik>
    <rptOwnerName>TEST OWNER</rptOwnerName>
    </reportingOwnerId>
    <reportingOwnerRelationship>
    <isDirector>1</isDirector>
    <isOfficer>1</isOfficer>
    <isTenPercentOwner>0</isTenPercentOwner>
    <isOther>0</isOther>
    <officerTitle>CEO</officerTitle>
    </reportingOwnerRelationship>
</reportingOwner>
<nonDerivativeTable>
    <nonDerivativeTransaction>
    <securityTitle>
        <value>Common Stock</value>
    </securityTitle>
    <transactionDate>
        <value>2025-05-14</value>
    </transactionDate>
    <transactionCoding>
        <transactionFormType>4</transactionFormType>
        <transactionCode>P</transactionCode>
        <equitySwapInvolved>0</equitySwapInvolved>
    </transactionCoding>
    <transactionAmounts>
        <transactionShares>
        <value>1000</value>
        </transactionShares>
        <transactionPricePerShare>
        <value>15.50</value>
        </transactionPricePerShare>
    </transactionAmounts>
    <ownershipNature>
        <directOrIndirectOwnership>
        <value>D</value>
        </directOrIndirectOwnership>
    </ownershipNature>
    </nonDerivativeTransaction>
</nonDerivativeTable>
</ownershipDocument>
</XML>
</TEXT>
</DOCUMENT>
"""

    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()

def test_form4_sgml_indexer_initialization():
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    assert indexer.cik == "0001234567"
    assert indexer.accession_number == "0001234567-25-000001"
    assert indexer.form_type == "4"

def test_form4_sgml_indexer_extract_issuer_data(sample_sgml_content):
    indexer = Form4SgmlIndexer(cik="0001084869", accession_number="0000921895-25-001190")
    issuer_data = indexer._extract_issuer_data(sample_sgml_content)

    # Verify we can extract issuer data from the sample
    assert issuer_data is not None, "Failed to extract issuer data"
    assert issuer_data.cik is not None, "Issuer CIK is missing"
    assert issuer_data.name is not None, "Issuer name is missing"
    assert issuer_data.entity_type == "company", "Issuer should be a company entity"
    
    # For the fixture file, we should find the specific issuer
    if "1 800 FLOWERS COM INC" in sample_sgml_content:
        # EntityData normalizes CIK by removing leading zeros
        assert issuer_data.cik == "1084869", "Expected CIK 1084869 for 1-800-FLOWERS"
        assert "FLOWERS" in issuer_data.name, "Expected issuer name to contain FLOWERS"

def test_form4_sgml_indexer_extract_reporting_owners(sample_sgml_content):
    indexer = Form4SgmlIndexer(cik="0001084869", accession_number="0000921895-25-001190")
    
    owners = indexer._extract_reporting_owners(sample_sgml_content)
    
    # Assert that we found at least one owner
    assert len(owners) > 0, "No reporting owners found"
    
    # Verify first owner's data
    owner = owners[0]
    assert owner["entity"] is not None, "Owner entity is missing"
    assert owner["entity"].cik is not None, "Owner CIK is missing"
    assert owner["entity"].name is not None, "Owner name is missing"
    assert owner["entity"].entity_type in ["person", "company"], "Invalid entity type"
    
    # Check that owners contain expected keys
    expected_keys = ["entity", "is_director", "is_officer", "is_ten_percent_owner", "is_other", "officer_title"]
    for key in expected_keys:
        assert key in owner, f"Owner data missing expected key: {key}"
        
    # If we have multiple owners (as in the sample file), check we found them all
    if "Fund 1 Investments" in sample_sgml_content:
        assert len(owners) >= 3, "Expected at least 3 owners for this sample"
        
        # Check for specific owner
        fund_owner = next((o for o in owners if "Fund 1" in o["entity"].name), None)
        assert fund_owner is not None, "Fund 1 Investments owner not found"

def test_form4_sgml_indexer_extract_xml_content(sample_sgml_content):
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    xml_content = indexer.extract_xml_content(sample_sgml_content)

    assert xml_content is not None
    assert "<ownershipDocument>" in xml_content

@patch('parsers.sgml.indexers.sgml_document_indexer.SgmlDocumentIndexer.index_documents')
def test_form4_sgml_indexer_index_documents(mock_super_index, sample_sgml_content):
    # Mock the parent class's index_documents method
    mock_super_index.return_value = [MagicMock()]

    indexer = Form4SgmlIndexer(cik="0001084869", accession_number="0000921895-25-001190")
    result = indexer.index_documents(sample_sgml_content)

    # Verify basic return structure
    assert "documents" in result, "Missing documents in result"
    assert "form4_data" in result, "Missing form4_data in result"
    assert "xml_content" in result, "Missing xml_content in result"
    assert result["xml_content"] is not None, "XML content is None"

    # Verify Form4FilingData
    form4_data = result["form4_data"]
    assert form4_data.accession_number is not None, "Missing accession number"
    
    # Check relationships
    assert hasattr(form4_data, "relationships"), "Missing relationships attribute"
    assert len(form4_data.relationships) > 0, "No relationships extracted"
    
    # Check relationship structure - using entity IDs now
    if len(form4_data.relationships) > 0:
        relationship = form4_data.relationships[0]
        assert hasattr(relationship, 'issuer_entity_id'), "Missing issuer_entity_id"
        assert hasattr(relationship, 'owner_entity_id'), "Missing owner_entity_id"
    
    # Check for relevant file data
    if "Fund 1 Investments" in sample_sgml_content:
        # For our fixture file, we expect multiple relationships and transactions
        assert form4_data.has_multiple_owners, "Expected multiple owners flag to be True"
        assert len(form4_data.relationships) >= 3, "Expected at least 3 relationships"
        
        # Verify that at least one relationship is a ten-percent owner
        ten_percent_relationship = next(
            (r for r in form4_data.relationships if getattr(r, 'is_ten_percent_owner', False)), 
            None
        )
        
        # First ensure we have relationships and then check if at least one is a ten-percent owner
        assert len(form4_data.relationships) > 0, "No relationships found"
        
        # Only check for this specific type if we have relationships
        if len(form4_data.relationships) > 0:
            assert ten_percent_relationship is not None, "Expected at least one ten-percent owner"
        
        # Check transactions exist and have correct security title
        assert hasattr(form4_data, "transactions"), "Missing transactions attribute"
        if len(form4_data.transactions) > 0:
            assert "Common Stock" in form4_data.transactions[0].security_title, "Expected Common Stock security"
            assert form4_data.transactions[0].transaction_code == "P", "Expected Purchase transaction code"

def test_extract_value_debug():
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")

    sample = """COMPANY DATA:
    COMPANY CONFORMED NAME:                   TEST ISSUER INC
    CENTRAL INDEX KEY:                                0001234567"""

    name = indexer._extract_value(sample, "COMPANY CONFORMED NAME:")
    assert name == "TEST ISSUER INC"

    cik = indexer._extract_value(sample, "CENTRAL INDEX KEY:")
    assert cik == "0001234567"
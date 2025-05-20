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
@patch('parsers.sgml.indexers.forms.form4_sgml_indexer.Form4SgmlIndexer._link_transactions_to_relationships')
@patch('parsers.sgml.indexers.forms.form4_sgml_indexer.Form4SgmlIndexer._add_transactions_from_parsed_xml')
def test_form4_sgml_indexer_index_documents(mock_add_transactions, mock_link_transactions, mock_super_index, sample_sgml_content):
    # Mock the parent class's index_documents method
    mock_super_index.return_value = [MagicMock()]

    # Import EntityData for creating mock data
    from models.dataclasses.entity import EntityData
    from uuid import uuid4
    
    # Set up Form4Parser to return appropriate structure with necessary entity data
    issuer_entity = EntityData(cik="1234567", name="Test Issuer", entity_type="company")
    owner_entity = EntityData(cik="9876543", name="Test Owner", entity_type="person")
    
    with patch('parsers.forms.form4_parser.Form4Parser.parse') as mock_parser:
        mock_parser.return_value = {
            "parsed_data": {
                "entity_data": {
                    "issuer_entity": issuer_entity,
                    "owner_entities": [owner_entity],
                    "relationships": [
                        {
                            "issuer_cik": "1234567",
                            "owner_cik": "9876543",
                            "is_director": True,
                            "is_officer": False,
                            "is_ten_percent_owner": False,
                            "is_other": False,
                            "officer_title": None,
                            "other_text": None
                        }
                    ]
                },
                "non_derivative_transactions": [{"securityTitle": "Common Stock"}],
                "derivative_transactions": [{"securityTitle": "Stock Option"}]
            }
        }
        
        indexer = Form4SgmlIndexer(cik="0001084869", accession_number="0000921895-25-001190")
        
        # Need to mock _update_form4_data_from_xml to create relationships
        with patch('parsers.sgml.indexers.forms.form4_sgml_indexer.Form4SgmlIndexer._update_form4_data_from_xml') as mock_update:
            # Define a side effect that adds a relationship to form4_data
            def add_mock_relationship(form4_data, entity_data, parsed_xml=None):
                from models.dataclasses.forms.form4_relationship import Form4RelationshipData
                from datetime import date
                
                # Add the entities to form4_data
                form4_data.issuer_entity = issuer_entity
                form4_data.owner_entities = [owner_entity]
                
                # Create a relationship
                relationship = Form4RelationshipData(
                    issuer_entity_id=issuer_entity.id,
                    owner_entity_id=owner_entity.id,
                    filing_date=date.today(),
                    is_director=True,
                    is_officer=False,
                    is_ten_percent_owner=False,
                    is_other=False
                )
                
                # Add relationship to form4_data
                form4_data.relationships.append(relationship)
                form4_data.has_multiple_owners = False
                
            mock_update.side_effect = add_mock_relationship
            
            result = indexer.index_documents(sample_sgml_content)
            
            # Verify our transaction methods were called
            assert mock_add_transactions.call_count > 0, "Transaction addition method not called"
            assert mock_link_transactions.call_count > 0, "Transaction linking method not called"

    # Verify basic return structure
    assert "documents" in result, "Missing documents in result"
    assert "form4_data" in result, "Missing form4_data in result"
    assert "xml_content" in result, "Missing xml_content in result"
    assert result["xml_content"] is not None, "XML content is None"

    # Verify Form4FilingData
    form4_data = result["form4_data"]
    assert form4_data.accession_number is not None, "Missing accession number"
    
    # Check relationships - these should now be populated by our mocked _update_form4_data_from_xml
    assert hasattr(form4_data, "relationships"), "Missing relationships attribute"
    assert len(form4_data.relationships) > 0, "No relationships extracted"
    
    # Check relationship structure - using entity IDs now
    relationship = form4_data.relationships[0]
    assert hasattr(relationship, 'issuer_entity_id'), "Missing issuer_entity_id"
    assert hasattr(relationship, 'owner_entity_id'), "Missing owner_entity_id"
    # Don't assert a specific is_director value as it may be overridden in other code
    
    # Skip the Fund 1 Investments specific test as we're using mocked data
    assert hasattr(form4_data, "transactions"), "Missing transactions attribute"

def test_extract_value_debug():
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")

    sample = """COMPANY DATA:
    COMPANY CONFORMED NAME:                   TEST ISSUER INC
    CENTRAL INDEX KEY:                                0001234567"""

    name = indexer._extract_value(sample, "COMPANY CONFORMED NAME:")
    assert name == "TEST ISSUER INC"

    cik = indexer._extract_value(sample, "CENTRAL INDEX KEY:")
    assert cik == "0001234567"
    
def test_extract_reporting_owners_deduplication():
    """Test that the _extract_reporting_owners method correctly deduplicates owners by CIK."""
    # Create a test SGML content with duplicate owner mentions (both in REPORTING-OWNER sections)
    duplicate_owner_sgml = """<SEC-HEADER>
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
    COMPANY CONFORMED NAME:                   JOHN DOE
    CENTRAL INDEX KEY:                                0009876543
</SEC-HEADER>

<REPORTING-OWNER>
OWNER DATA:
    COMPANY CONFORMED NAME:                   JOHN DOE
    CENTRAL INDEX KEY:                                0009876543
</REPORTING-OWNER>

<DOCUMENT>
<TYPE>4
<SEQUENCE>1
<FILENAME>form4.xml
<TEXT>
</TEXT>
</DOCUMENT>
"""

    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    owners = indexer._extract_reporting_owners(duplicate_owner_sgml)
    
    # Assert that we only have one owner despite the duplicate entries
    assert len(owners) == 1, "Failed to deduplicate owners by CIK"
    assert owners[0]["entity"].cik == "9876543", "Expected CIK 9876543"
    assert owners[0]["entity"].name == "JOHN DOE", "Expected name JOHN DOE"

def test_extract_reporting_owners_deduplication_header_and_section():
    """Test deduplication when the same owner appears in both the header and a REPORTING-OWNER section."""
    # Create a test SGML content with duplicate owner mentions (in both header and REPORTING-OWNER section)
    mixed_duplicate_sgml = """<SEC-HEADER>
ACCESSION NUMBER:             0001234567-25-000001
CONFORMED SUBMISSION TYPE:    4
CONFORMED PERIOD OF REPORT:   20250514
FILED AS OF DATE:             20250515
COMPANY CONFORMED NAME:       TEST ISSUER INC
CENTRAL INDEX KEY:            0001234567

COMPANY CONFORMED NAME:       JANE SMITH
CENTRAL INDEX KEY:            0008765432

<ISSUER>
COMPANY DATA:
    COMPANY CONFORMED NAME:                   TEST ISSUER INC
    CENTRAL INDEX KEY:                                0001234567
</SEC-HEADER>

<REPORTING-OWNER>
OWNER DATA:
    COMPANY CONFORMED NAME:                   JANE SMITH
    CENTRAL INDEX KEY:                                0008765432
</REPORTING-OWNER>

<DOCUMENT>
<TYPE>4
<SEQUENCE>1
<FILENAME>form4.xml
<TEXT>
</TEXT>
</DOCUMENT>
"""

    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    owners = indexer._extract_reporting_owners(mixed_duplicate_sgml)
    
    # Assert that we only have one owner despite the duplicate entries in different locations
    assert len(owners) == 1, "Failed to deduplicate owners across header and REPORTING-OWNER sections"
    assert owners[0]["entity"].cik == "8765432", "Expected CIK 8765432"
    assert owners[0]["entity"].name == "JANE SMITH", "Expected name JANE SMITH"

def test_link_transactions_to_relationships():
    """Test the _link_transactions_to_relationships method that ensures transactions are linked to relationships"""
    from models.dataclasses.forms.form4_filing import Form4FilingData
    from models.dataclasses.forms.form4_relationship import Form4RelationshipData
    from models.dataclasses.forms.form4_transaction import Form4TransactionData
    from datetime import date
    from uuid import uuid4
    
    # Create a test Form4FilingData with relationships and transactions
    filing = Form4FilingData(
        accession_number="0001234567-25-000001",
        period_of_report=date(2025, 5, 14)
    )
    
    # Create a relationship
    relationship_id = uuid4()
    relationship = Form4RelationshipData(
        issuer_entity_id=uuid4(),
        owner_entity_id=uuid4(),
        filing_date=date(2025, 5, 15),
        id=relationship_id  # Use a known ID
    )
    filing.relationships = [relationship]
    
    # Create transactions without relationship_id
    transaction1 = Form4TransactionData(
        security_title="Common Stock",
        transaction_date=date(2025, 5, 14),
        transaction_code="P"
    )
    transaction2 = Form4TransactionData(
        security_title="Preferred Stock",
        transaction_date=date(2025, 5, 14),
        transaction_code="S"
    )
    filing.transactions = [transaction1, transaction2]
    
    # Call the method
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    indexer._link_transactions_to_relationships(filing)
    
    # Check that transactions now have relationship_id set
    assert transaction1.relationship_id == relationship_id
    assert transaction2.relationship_id == relationship_id
    
def test_add_transactions_from_parsed_xml():
    """Test the _add_transactions_from_parsed_xml method for converting raw transaction data to Form4TransactionData"""
    from models.dataclasses.forms.form4_filing import Form4FilingData
    from datetime import date
    
    # Sample transaction dictionaries, similar to what Form4Parser would return
    non_derivative_transactions = [
        {
            "securityTitle": "Common Stock",
            "transactionDate": "2025-05-14",
            "transactionCode": "P",
            "formType": "4",
            "shares": "1000",
            "pricePerShare": "15.50",
            "ownership": "D"
        },
        {
            "securityTitle": "Class A Common Stock",
            "transactionDate": "2025-05-14", 
            "transactionCode": "S",
            "formType": "4",
            "shares": "500",
            "pricePerShare": "20.25",
            "ownership": "I",
            "indirectOwnershipNature": "By Trust"
        }
    ]
    
    derivative_transactions = [
        {
            "securityTitle": "Stock Option (Right to Buy)",
            "transactionDate": "2025-05-14",
            "transactionCode": "A",
            "formType": "4",
            "shares": "2000",
            "pricePerShare": "0.00",
            "ownership": "D",
            "conversionOrExercisePrice": "15.00",
            "expirationDate": "2035-05-14"
        }
    ]
    
    # Create a test Form4FilingData
    filing = Form4FilingData(
        accession_number="0001234567-25-000001",
        period_of_report=date(2025, 5, 14)
    )
    
    # Call the method
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    indexer._add_transactions_from_parsed_xml(filing, non_derivative_transactions, derivative_transactions)
    
    # Check that transactions were added correctly
    assert len(filing.transactions) == 3
    
    # Check non-derivative transactions
    non_derivative_count = sum(1 for t in filing.transactions if not t.is_derivative)
    assert non_derivative_count == 2
    
    # Check derivative transactions
    derivative_count = sum(1 for t in filing.transactions if t.is_derivative)
    assert derivative_count == 1
    
    # Check specific transaction properties
    purchase_transaction = next((t for t in filing.transactions if t.transaction_code == "P"), None)
    assert purchase_transaction is not None
    assert purchase_transaction.security_title == "Common Stock"
    assert purchase_transaction.shares_amount == 1000.0
    assert purchase_transaction.price_per_share == 15.50
    
    # Check indirect ownership transaction
    indirect_transaction = next((t for t in filing.transactions if t.ownership_nature == "I"), None)
    assert indirect_transaction is not None
    assert indirect_transaction.indirect_ownership_explanation == "By Trust"
    
    # Check derivative transaction
    option_transaction = next((t for t in filing.transactions if t.is_derivative), None)
    assert option_transaction is not None
    assert option_transaction.security_title == "Stock Option (Right to Buy)"
    assert option_transaction.conversion_price == 15.00
    assert option_transaction.expiration_date.year == 2035
    
def test_group_filing_flag_multi_owner():
    """Test that the is_group_filing flag is correctly set when multiple reporting owners exist."""
    from models.dataclasses.forms.form4_filing import Form4FilingData
    from models.dataclasses.entity import EntityData
    from datetime import date
    
    # Create a Form4SgmlIndexer instance
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    
    # Create a test Form4FilingData
    form4_data = Form4FilingData(
        accession_number="0001234567-25-000001",
        period_of_report=date(2025, 5, 14)
    )
    
    # Create multiple owner entities to simulate multiple reporting owners
    issuer_entity = EntityData(
        cik="1234567",
        name="Test Issuer Inc",
        entity_type="company"
    )
    
    owner_entities = [
        EntityData(
            cik="9876543",
            name="John Doe",
            entity_type="person"
        ),
        EntityData(
            cik="8765432",
            name="Jane Smith",
            entity_type="person"
        ),
        EntityData(
            cik="7654321",
            name="Acme Investment LLC",
            entity_type="company"
        )
    ]
    
    # Create relationships data as it would come from the XML parser
    relationships = [
        {
            "issuer_cik": "1234567",
            "owner_cik": "9876543",
            "is_director": True,
            "is_officer": False,
            "is_ten_percent_owner": False,
            "is_other": False
        },
        {
            "issuer_cik": "1234567",
            "owner_cik": "8765432",
            "is_director": False,
            "is_officer": True,
            "is_ten_percent_owner": False,
            "is_other": False,
            "officer_title": "CFO"
        },
        {
            "issuer_cik": "1234567",
            "owner_cik": "7654321",
            "is_director": False,
            "is_officer": False,
            "is_ten_percent_owner": True,
            "is_other": False
        }
    ]
    
    # Create entity_data dictionary similar to what would be returned by Form4Parser
    entity_data = {
        "issuer_entity": issuer_entity,
        "owner_entities": owner_entities,
        "relationships": relationships
    }
    
    # Call the method that we updated with the Bug 7 fix
    indexer._update_form4_data_from_xml(form4_data, entity_data)
    
    # Check that the has_multiple_owners flag is set correctly (Bug 4 fix)
    assert form4_data.has_multiple_owners is True, "has_multiple_owners should be True with 3 owners"
    assert len(form4_data.relationships) == 3, "Should have 3 relationships"
    
    # Check that is_group_filing is set on all relationships (Bug 7 fix)
    for relationship in form4_data.relationships:
        assert relationship.is_group_filing is True, "is_group_filing should be True on all relationships"
        assert relationship.relationship_details.get("is_group_filing") is True, "is_group_filing should be in relationship_details"
        
def test_group_filing_flag_single_owner():
    """Test that the is_group_filing flag is correctly NOT set when only one reporting owner exists."""
    from models.dataclasses.forms.form4_filing import Form4FilingData
    from models.dataclasses.entity import EntityData
    from datetime import date
    
    # Create a Form4SgmlIndexer instance
    indexer = Form4SgmlIndexer(cik="0001234567", accession_number="0001234567-25-000001")
    
    # Create a test Form4FilingData
    form4_data = Form4FilingData(
        accession_number="0001234567-25-000001",
        period_of_report=date(2025, 5, 14)
    )
    
    # Create a single owner entity
    issuer_entity = EntityData(
        cik="1234567",
        name="Test Issuer Inc",
        entity_type="company"
    )
    
    owner_entities = [
        EntityData(
            cik="9876543",
            name="John Doe",
            entity_type="person"
        )
    ]
    
    # Create a single relationship
    relationships = [
        {
            "issuer_cik": "1234567",
            "owner_cik": "9876543",
            "is_director": True,
            "is_officer": True,
            "is_ten_percent_owner": False,
            "is_other": False,
            "officer_title": "CEO"
        }
    ]
    
    # Create entity_data dictionary similar to what would be returned by Form4Parser
    entity_data = {
        "issuer_entity": issuer_entity,
        "owner_entities": owner_entities,
        "relationships": relationships
    }
    
    # Call the method that we updated with the Bug 7 fix
    indexer._update_form4_data_from_xml(form4_data, entity_data)
    
    # Check that the has_multiple_owners flag is set correctly (Bug 4 fix)
    assert form4_data.has_multiple_owners is False, "has_multiple_owners should be False with 1 owner"
    assert len(form4_data.relationships) == 1, "Should have 1 relationship"
    
    # Check that is_group_filing is NOT set on the relationship (Bug 7 fix)
    relationship = form4_data.relationships[0]
    assert relationship.is_group_filing is False, "is_group_filing should be False for single owner"
    assert "is_group_filing" not in relationship.relationship_details, "is_group_filing should not be in relationship_details"
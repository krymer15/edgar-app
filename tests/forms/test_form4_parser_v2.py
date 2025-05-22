# tests/forms/test_form4_parser_v2.py
import pytest
import uuid
from unittest.mock import MagicMock, Mock
from datetime import date
from decimal import Decimal

from parsers.forms.form4_parser_v2 import Form4ParserV2
from models.dataclasses.forms.form4_filing_context import Form4FilingContext
from models.dataclasses.entity import EntityData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from models.dataclasses.forms.position_data import RelationshipPositionData


# Mock Services for Testing
class MockSecurityService:
    def __init__(self):
        self.security_counter = 0
        
    def get_or_create_security(self, security_data):
        self.security_counter += 1
        return f"security_{self.security_counter}"
        
    def get_or_create_derivative_security(self, derivative_data):
        self.security_counter += 1
        return f"derivative_{self.security_counter}"


class MockTransactionService:
    def __init__(self):
        self.transaction_counter = 0
        
    def create_transaction(self, transaction_data):
        self.transaction_counter += 1
        return f"transaction_{self.transaction_counter}"


class MockPositionService:
    def __init__(self):
        self.position_counter = 0
        
    def update_position_from_transaction(self, transaction_data):
        self.position_counter += 1
        return f"position_{self.position_counter}"
        
    def create_position_only_entry(self, position_data):
        self.position_counter += 1
        return f"position_only_{self.position_counter}"


@pytest.fixture
def mock_services():
    return {
        'security_service': MockSecurityService(),
        'transaction_service': MockTransactionService(),
        'position_service': MockPositionService()
    }


@pytest.fixture  
def parser(mock_services):
    return Form4ParserV2(**mock_services)


@pytest.fixture
def sample_filing_context():
    return Form4FilingContext(
        accession_number="0001610717-23-000035",
        cik="0001770787",
        filing_date=date(2023, 5, 11)
    )


@pytest.fixture
def basic_form4_xml():
    return """<?xml version="1.0"?>
<ownershipDocument>
    <schemaVersion>X0407</schemaVersion>
    <documentType>4</documentType>
    <periodOfReport>2023-05-11</periodOfReport>
    
    <issuer>
        <issuerCik>0001770787</issuerCik>
        <issuerName>10x Genomics, Inc.</issuerName>
        <issuerTradingSymbol>TXG</issuerTradingSymbol>
    </issuer>
    
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerCik>0001421050</rptOwnerCik>
            <rptOwnerName>Mammen Mathai</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isDirector>true</isDirector>
        </reportingOwnerRelationship>
    </reportingOwner>
    
    <nonDerivativeTable>
        <nonDerivativeTransaction>
            <securityTitle>
                <value>Class A Common Stock</value>
            </securityTitle>
            <transactionDate>
                <value>2023-05-11</value>
            </transactionDate>
            <transactionCoding>
                <transactionFormType>4</transactionFormType>
                <transactionCode>M</transactionCode>
                <equitySwapInvolved>0</equitySwapInvolved>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares>
                    <value>1000</value>
                </transactionShares>
                <transactionPricePerShare>
                    <value>25.50</value>
                </transactionPricePerShare>
                <transactionAcquiredDisposedCode>
                    <value>A</value>
                </transactionAcquiredDisposedCode>
            </transactionAmounts>
            <ownershipNature>
                <directOrIndirectOwnership>
                    <value>D</value>
                </directOrIndirectOwnership>
            </ownershipNature>
        </nonDerivativeTransaction>
    </nonDerivativeTable>
</ownershipDocument>"""


@pytest.fixture
def multiple_owners_xml():
    return """<?xml version="1.0"?>
<ownershipDocument>
    <schemaVersion>X0407</schemaVersion>
    <documentType>4</documentType>
    <periodOfReport>2023-05-11</periodOfReport>
    
    <issuer>
        <issuerCik>0001750019</issuerCik>
        <issuerName>Test Company Inc.</issuerName>
        <issuerTradingSymbol>TEST</issuerTradingSymbol>
    </issuer>
    
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerCik>0001421050</rptOwnerCik>
            <rptOwnerName>John Smith</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isDirector>true</isDirector>
        </reportingOwnerRelationship>
    </reportingOwner>
    
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerCik>0001421051</rptOwnerCik>
            <rptOwnerName>Jane Doe</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isOfficer>true</isOfficer>
            <officerTitle>CEO</officerTitle>
        </reportingOwnerRelationship>
    </reportingOwner>
    
    <!-- Duplicate owner should be filtered out -->
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerCik>0001421050</rptOwnerCik>
            <rptOwnerName>John Smith Duplicate</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isOther>true</isOther>
            <otherText>Some other role</otherText>
        </reportingOwnerRelationship>
    </reportingOwner>
</ownershipDocument>"""


@pytest.fixture
def derivative_transaction_xml():
    return """<?xml version="1.0"?>
<ownershipDocument>
    <schemaVersion>X0407</schemaVersion>
    <documentType>4</documentType>
    <periodOfReport>2023-05-11</periodOfReport>
    
    <issuer>
        <issuerCik>0001770787</issuerCik>
        <issuerName>10x Genomics, Inc.</issuerName>
        <issuerTradingSymbol>TXG</issuerTradingSymbol>
    </issuer>
    
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerCik>0001421050</rptOwnerCik>
            <rptOwnerName>Mammen Mathai</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isDirector>true</isDirector>
        </reportingOwnerRelationship>
    </reportingOwner>
    
    <derivativeTable>
        <derivativeTransaction>
            <securityTitle>
                <value>Stock Option</value>
            </securityTitle>
            <conversionOrExercisePrice>
                <value>15.00</value>
            </conversionOrExercisePrice>
            <transactionDate>
                <value>2023-05-11</value>
            </transactionDate>
            <transactionCoding>
                <transactionFormType>4</transactionFormType>
                <transactionCode>A</transactionCode>
                <equitySwapInvolved>0</equitySwapInvolved>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares>
                    <value>500</value>
                </transactionShares>
                <transactionAcquiredDisposedCode>
                    <value>A</value>
                </transactionAcquiredDisposedCode>
            </transactionAmounts>
            <exerciseDate>
                <value>2024-05-11</value>
            </exerciseDate>
            <expirationDate>
                <value>2033-05-11</value>
            </expirationDate>
            <underlyingSecurity>
                <underlyingSecurityTitle>
                    <value>Class A Common Stock</value>
                </underlyingSecurityTitle>
                <underlyingSecurityShares>
                    <value>500</value>
                </underlyingSecurityShares>
            </underlyingSecurity>
            <ownershipNature>
                <directOrIndirectOwnership>
                    <value>D</value>
                </directOrIndirectOwnership>
            </ownershipNature>
        </derivativeTransaction>
    </derivativeTable>
</ownershipDocument>"""


@pytest.fixture
def position_holdings_xml():
    return """<?xml version="1.0"?>
<ownershipDocument>
    <schemaVersion>X0407</schemaVersion>
    <documentType>4</documentType>
    <periodOfReport>2023-05-11</periodOfReport>
    
    <issuer>
        <issuerCik>0001770787</issuerCik>
        <issuerName>10x Genomics, Inc.</issuerName>
        <issuerTradingSymbol>TXG</issuerTradingSymbol>
    </issuer>
    
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerCik>0001421050</rptOwnerCik>
            <rptOwnerName>Mammen Mathai</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isDirector>true</isDirector>
        </reportingOwnerRelationship>
    </reportingOwner>
    
    <nonDerivativeTable>
        <nonDerivativeHolding>
            <securityTitle>
                <value>Class A Common Stock</value>
            </securityTitle>
            <postTransactionAmounts>
                <sharesOwnedFollowingTransaction>
                    <value>5000</value>
                </sharesOwnedFollowingTransaction>
            </postTransactionAmounts>
            <ownershipNature>
                <directOrIndirectOwnership>
                    <value>D</value>
                </directOrIndirectOwnership>
            </ownershipNature>
        </nonDerivativeHolding>
    </nonDerivativeTable>
    
    <derivativeTable>
        <derivativeHolding>
            <securityTitle>
                <value>Stock Option</value>
            </securityTitle>
            <postTransactionAmounts>
                <sharesOwnedFollowingTransaction>
                    <value>1500</value>
                </sharesOwnedFollowingTransaction>
            </postTransactionAmounts>
            <exerciseDate>
                <value>2024-05-11</value>
            </exerciseDate>
            <expirationDate>
                <value>2033-05-11</value>
            </expirationDate>
            <underlyingSecurity>
                <underlyingSecurityTitle>
                    <value>Class A Common Stock</value>
                </underlyingSecurityTitle>
            </underlyingSecurity>
            <ownershipNature>
                <directOrIndirectOwnership>
                    <value>I</value>
                </directOrIndirectOwnership>
                <natureOfOwnership>
                    <value>By Trust</value>
                </natureOfOwnership>
            </ownershipNature>
        </derivativeHolding>
    </derivativeTable>
</ownershipDocument>"""


class TestForm4ParserV2:
    """Test cases for Form4ParserV2"""
    
    def test_parse_basic_form4(self, parser, basic_form4_xml, sample_filing_context):
        """Test basic Form 4 parsing with single owner and transaction"""
        result = parser.parse(basic_form4_xml, sample_filing_context)
        
        assert result["success"] is True
        assert result["filing_id"] == sample_filing_context.accession_number
        
        # Check entities
        entities = result["entities"]
        assert entities["issuer"] is not None
        assert entities["issuer"]["data"].name == "10x Genomics, Inc."
        assert entities["issuer"]["data"].cik == "1770787"  # Leading zeros removed
        assert len(entities["owners"]) == 1
        assert entities["owners"][0]["data"].name == "Mammen Mathai"
        assert entities["owners"][0]["data"].cik == "1421050"
        assert len(entities["relationships"]) == 1
        assert entities["relationships"][0].is_director is True
        
        # Check securities
        assert len(result["securities"]) == 1
        
        # Check transactions
        assert len(result["transactions"]) == 1
        
        # Check metadata
        metadata = result["metadata"]
        assert metadata["document_type"] == "4"
        assert metadata["schema_version"] == "X0407"
        assert metadata["non_derivative_transactions"] == 1
        assert metadata["derivative_transactions"] == 0
    
    def test_parse_multiple_owners_with_deduplication(self, parser, multiple_owners_xml, sample_filing_context):
        """Test parsing with multiple owners and deduplication"""
        result = parser.parse(multiple_owners_xml, sample_filing_context)
        
        assert result["success"] is True
        
        entities = result["entities"]
        # Should have 2 unique owners, not 3 (due to deduplication)
        assert len(entities["owners"]) == 2
        assert len(entities["relationships"]) == 2
        
        # Check first owner (director)
        owner1 = entities["owners"][0]["data"]
        assert owner1.name == "John Smith"
        assert owner1.cik == "1421050"
        rel1 = entities["relationships"][0]
        assert rel1.is_director is True
        assert rel1.relationship_type == "director"
        
        # Check second owner (officer)
        owner2 = entities["owners"][1]["data"]
        assert owner2.name == "Jane Doe"
        assert owner2.cik == "1421051"
        rel2 = entities["relationships"][1]
        assert rel2.is_officer is True
        assert rel2.officer_title == "CEO"
        assert rel2.relationship_type == "officer"
    
    def test_parse_derivative_transaction(self, parser, derivative_transaction_xml, sample_filing_context):
        """Test parsing derivative transactions"""
        result = parser.parse(derivative_transaction_xml, sample_filing_context)
        
        assert result["success"] is True
        
        # Should have both base security and derivative security
        assert len(result["securities"]) == 2  # "Stock Option" and "Stock Option_derivative"
        
        # Check transactions
        assert len(result["transactions"]) == 1
        
        metadata = result["metadata"]
        assert metadata["derivative_transactions"] == 1
        assert metadata["non_derivative_transactions"] == 0
    
    def test_parse_position_holdings(self, parser, position_holdings_xml, sample_filing_context):
        """Test parsing position-only holdings"""
        result = parser.parse(position_holdings_xml, sample_filing_context)
        
        assert result["success"] is True
        
        # Check positions
        assert len(result["positions"]) == 2  # Non-derivative and derivative holdings
        
        metadata = result["metadata"]
        assert metadata["non_derivative_holdings"] == 1
        assert metadata["derivative_holdings"] == 1
        assert metadata["non_derivative_transactions"] == 0
        assert metadata["derivative_transactions"] == 0
    
    def test_entity_type_classification(self, parser):
        """Test entity type classification heuristics"""
        # Test person classification
        assert parser._classify_entity_type("John Smith") == "person"
        assert parser._classify_entity_type("Jane Doe Jr.") == "person"
        
        # Test company classification
        assert parser._classify_entity_type("Apple Inc.") == "company"
        assert parser._classify_entity_type("Microsoft Corp") == "company"
        assert parser._classify_entity_type("Investment Trust LLC") == "company"
        assert parser._classify_entity_type("Private Partners LP") == "company"
        assert parser._classify_entity_type("Hedge Fund") == "company"
        
        # Test edge cases
        assert parser._classify_entity_type("") == "company"  # Default
        assert parser._classify_entity_type(None) == "company"
    
    def test_boolean_flag_parsing(self, parser):
        """Test robust boolean flag parsing"""
        from xml.etree import ElementTree as ET
        
        # Test "true"/"false" format
        xml1 = "<root><isDirector>true</isDirector></root>"
        root1 = ET.fromstring(xml1)
        assert parser._parse_boolean_flag(root1, "isDirector") is True
        
        xml2 = "<root><isDirector>false</isDirector></root>"
        root2 = ET.fromstring(xml2)
        assert parser._parse_boolean_flag(root2, "isDirector") is False
        
        # Test "1"/"0" format
        xml3 = "<root><isOfficer>1</isOfficer></root>"
        root3 = ET.fromstring(xml3)
        assert parser._parse_boolean_flag(root3, "isOfficer") is True
        
        xml4 = "<root><isOfficer>0</isOfficer></root>"
        root4 = ET.fromstring(xml4)
        assert parser._parse_boolean_flag(root4, "isOfficer") is False
        
        # Test missing element
        xml5 = "<root></root>"
        root5 = ET.fromstring(xml5)
        assert parser._parse_boolean_flag(root5, "isMissing") is False
    
    def test_date_parsing_robust(self, parser):
        """Test robust date parsing with multiple formats"""
        # XML format (most common)
        assert parser._parse_date_safely("2023-05-11") == date(2023, 5, 11)
        
        # SGML format
        assert parser._parse_date_safely("20230511") == date(2023, 5, 11)
        
        # Other formats
        assert parser._parse_date_safely("05/11/2023") == date(2023, 5, 11)
        assert parser._parse_date_safely("05-11-2023") == date(2023, 5, 11)
        assert parser._parse_date_safely("2023/05/11") == date(2023, 5, 11)
        
        # Invalid formats
        assert parser._parse_date_safely("invalid") is None
        assert parser._parse_date_safely("") is None
        assert parser._parse_date_safely(None) is None
    
    def test_decimal_extraction_safe(self, parser):
        """Test safe decimal extraction"""
        from xml.etree import ElementTree as ET
        
        # Valid decimal
        xml1 = "<root><amount><value>123.45</value></amount></root>"
        root1 = ET.fromstring(xml1)
        result = parser._get_decimal(root1, "amount/value")
        assert result == Decimal("123.45")
        
        # Integer
        xml2 = "<root><amount><value>1000</value></amount></root>"
        root2 = ET.fromstring(xml2)
        result = parser._get_decimal(root2, "amount/value")
        assert result == Decimal("1000")
        
        # Invalid decimal
        xml3 = "<root><amount><value>invalid</value></amount></root>"
        root3 = ET.fromstring(xml3)
        result = parser._get_decimal(root3, "amount/value")
        assert result is None
        
        # Missing element
        xml4 = "<root></root>"
        root4 = ET.fromstring(xml4)
        result = parser._get_decimal(root4, "missing/value")
        assert result is None
    
    def test_footnote_extraction(self, parser):
        """Test comprehensive footnote extraction"""
        from xml.etree import ElementTree as ET
        
        xml = """<transaction>
            <footnoteId id="F1"/>
            <securityTitle footnoteId="F2">
                <value>Stock</value>
                <footnoteId id="F3"/>
            </securityTitle>
            <amount>
                <value>1000</value>
                <footnoteId id="F4"/>
            </amount>
        </transaction>"""
        
        root = ET.fromstring(xml)
        footnotes = parser._extract_footnote_ids(root)
        
        # Should find all footnote IDs
        assert "F1" in footnotes
        assert "F2" in footnotes
        assert "F3" in footnotes
        assert "F4" in footnotes
        assert len(footnotes) == 4
    
    def test_error_handling_invalid_xml(self, parser, sample_filing_context):
        """Test error handling for invalid XML"""
        invalid_xml = "<invalid><unclosed>content</invalid>"
        
        result = parser.parse(invalid_xml, sample_filing_context)
        
        assert result["success"] is False
        assert "error" in result
        assert result["filing_context"] == sample_filing_context
    
    def test_missing_required_fields(self, parser, sample_filing_context):
        """Test handling of missing required fields"""
        # XML missing issuer
        xml_no_issuer = """<?xml version="1.0"?>
        <ownershipDocument>
            <documentType>4</documentType>
            <reportingOwner>
                <reportingOwnerId>
                    <rptOwnerCik>0001421050</rptOwnerCik>
                    <rptOwnerName>Test Owner</rptOwnerName>
                </reportingOwnerId>
                <reportingOwnerRelationship>
                    <isDirector>true</isDirector>
                </reportingOwnerRelationship>
            </reportingOwner>
        </ownershipDocument>"""
        
        result = parser.parse(xml_no_issuer, sample_filing_context)
        
        # Should still succeed but with warning logged
        assert result["success"] is True
        assert result["entities"]["issuer"] is None
        
    def test_relationship_type_determination(self, parser):
        """Test relationship type determination logic"""
        # Director priority
        assert parser._determine_relationship_type(True, True, True, True) == "director"
        
        # Officer second priority  
        assert parser._determine_relationship_type(False, True, True, True) == "officer"
        
        # 10% owner third priority
        assert parser._determine_relationship_type(False, False, True, True) == "10_percent_owner"
        
        # Other as fallback
        assert parser._determine_relationship_type(False, False, False, True) == "other"
        assert parser._determine_relationship_type(False, False, False, False) == "other"
    
    def test_service_integration_called(self, parser, basic_form4_xml, sample_filing_context):
        """Test that services are properly called during parsing"""
        result = parser.parse(basic_form4_xml, sample_filing_context)
        
        assert result["success"] is True
        
        # Verify mock services were called
        assert parser.security_service.security_counter > 0
        assert parser.transaction_service.transaction_counter > 0
        assert parser.position_service.position_counter > 0
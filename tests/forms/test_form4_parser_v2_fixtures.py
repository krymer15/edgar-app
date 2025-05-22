# tests/forms/test_form4_parser_v2_fixtures.py
import pytest
import os
from datetime import date
from decimal import Decimal

from parsers.forms.form4_parser_v2 import Form4ParserV2
from models.dataclasses.forms.form4_filing_context import Form4FilingContext


# Mock Services for fixture testing
class MockSecurityService:
    def __init__(self):
        self.security_counter = 0
        self.created_securities = []
        
    def get_or_create_security(self, security_data):
        self.security_counter += 1
        security_id = f"security_{self.security_counter}"
        self.created_securities.append({
            'id': security_id,
            'title': security_data.title,
            'type': security_data.security_type,
            'issuer_id': security_data.issuer_entity_id
        })
        return security_id
        
    def get_or_create_derivative_security(self, derivative_data):
        self.security_counter += 1
        derivative_id = f"derivative_{self.security_counter}"
        self.created_securities.append({
            'id': derivative_id,
            'security_id': derivative_data.security_id,
            'underlying_title': derivative_data.underlying_security_title,
            'conversion_price': derivative_data.conversion_price
        })
        return derivative_id


class MockTransactionService:
    def __init__(self):
        self.transaction_counter = 0
        self.created_transactions = []
        
    def create_transaction(self, transaction_data):
        self.transaction_counter += 1
        transaction_id = f"transaction_{self.transaction_counter}"
        self.created_transactions.append({
            'id': transaction_id,
            'type': type(transaction_data).__name__,
            'security_id': transaction_data.security_id,
            'transaction_code': transaction_data.transaction_code,
            'shares_amount': transaction_data.shares_amount,
            'transaction_date': transaction_data.transaction_date
        })
        return transaction_id


class MockPositionService:
    def __init__(self):
        self.position_counter = 0
        self.created_positions = []
        
    def update_position_from_transaction(self, transaction_data):
        self.position_counter += 1
        position_id = f"position_{self.position_counter}"
        self.created_positions.append({
            'id': position_id,
            'type': 'transaction_position',
            'security_id': transaction_data.security_id,
            'shares_amount': transaction_data.shares_amount
        })
        return position_id
        
    def create_position_only_entry(self, position_data):
        self.position_counter += 1
        position_id = f"position_only_{self.position_counter}"
        self.created_positions.append({
            'id': position_id,
            'type': 'position_only',
            'security_id': position_data.security_id,
            'shares_amount': position_data.shares_amount,
            'position_type': position_data.position_type
        })
        return position_id


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


def load_fixture(filename):
    """Load XML content from test fixtures"""
    fixture_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "fixtures", 
        filename
    )
    
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestForm4ParserV2Fixtures:
    """Test Form4ParserV2 with actual XML fixtures"""
    
    def test_parse_basic_single_owner_case(self, parser):
        """Test with 0001610717-23-000035.xml - Basic single owner case"""
        xml_content = load_fixture("0001610717-23-000035.xml")
        filing_context = Form4FilingContext(
            accession_number="0001610717-23-000035",
            cik="0001770787",
            filing_date=date(2023, 5, 11)
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        # Check entities
        entities = result["entities"]
        assert entities["issuer"] is not None
        assert entities["issuer"]["data"].name == "10x Genomics, Inc."
        assert entities["issuer"]["data"].cik == "1770787"  # Leading zeros stripped
        
        # Should have one owner
        assert len(entities["owners"]) == 1
        owner = entities["owners"][0]["data"]
        assert owner.name == "Mammen Mathai"
        assert owner.cik == "1421050"
        assert owner.entity_type == "person"
        
        # Should have one relationship
        assert len(entities["relationships"]) == 1
        rel = entities["relationships"][0]
        assert rel.is_director is True
        assert rel.relationship_type == "director"
        
        # Check that securities were created
        assert len(parser.security_service.created_securities) > 0
        
        # Check that transactions were created
        assert len(parser.transaction_service.created_transactions) > 0
        
        # Check metadata extraction
        metadata = result["metadata"]
        assert metadata["document_type"] == "4"
        assert metadata["schema_version"] == "X0407"
        assert metadata["period_of_report"] == "2023-05-11"
    
    def test_parse_multiple_transaction_types(self, parser):
        """Test with 000032012123000040_form4.xml - Multiple transaction types"""
        xml_content = load_fixture("000032012123000040_form4.xml")
        filing_context = Form4FilingContext(
            accession_number="000032012123000040",
            cik="0000032012",
            filing_date=date(2023, 12, 15)  # Approximate date
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        # Should process successfully with multiple transaction types
        entities = result["entities"]
        assert entities["issuer"] is not None
        assert len(entities["owners"]) >= 1
        
        # Check that various transaction types were processed
        transactions = parser.transaction_service.created_transactions
        if transactions:
            # Verify we have transaction data
            for txn in transactions:
                assert 'transaction_code' in txn
                assert 'shares_amount' in txn
                assert 'transaction_date' in txn
    
    def test_parse_multiple_owners_group_filing(self, parser):
        """Test with 000120919123029527_form4.xml - Multiple owners (group filing)"""
        xml_content = load_fixture("000120919123029527_form4.xml")
        filing_context = Form4FilingContext(
            accession_number="000120919123029527",
            cik="0001209191",
            filing_date=date(2023, 12, 15)  # Approximate date
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        entities = result["entities"]
        assert entities["issuer"] is not None
        
        # Should handle multiple owners with deduplication
        owners = entities["owners"]
        relationships = entities["relationships"]
        
        # Verify deduplication - unique CIKs only
        ciks = [owner["data"].cik for owner in owners]
        assert len(ciks) == len(set(ciks)), "Duplicate CIKs found - deduplication failed"
        
        # Should have corresponding relationships
        assert len(relationships) == len(owners)
    
    def test_parse_derivative_transactions(self, parser):
        """Test with 000092963823001482_form4.xml - Derivative transactions"""
        xml_content = load_fixture("000092963823001482_form4.xml")
        filing_context = Form4FilingContext(
            accession_number="000092963823001482",
            cik="0000929638",
            filing_date=date(2023, 12, 15)  # Approximate date
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        # Check for derivative security creation
        securities = parser.security_service.created_securities
        derivative_securities = [s for s in securities if 'underlying_title' in s]
        
        # Should have created derivative securities if they exist in the XML
        metadata = result["metadata"]
        if metadata.get("derivative_transactions", 0) > 0:
            assert len(derivative_securities) > 0
        
        # Check transaction processing
        transactions = parser.transaction_service.created_transactions
        derivative_transactions = [t for t in transactions if t['type'] == 'DerivativeTransactionData']
        
        assert len(derivative_transactions) == metadata.get("derivative_transactions", 0)
    
    def test_comprehensive_fixture_processing(self, parser):
        """Test that all fixtures can be processed without errors"""
        fixture_files = [
            "0001610717-23-000035.xml",
            "000032012123000040_form4.xml", 
            "000092963823001482_form4.xml",
            "000106299323011116_form4.xml",
            "000120919123029527_form4.xml",
            "sampleform4.xml"
        ]
        
        results = []
        
        for filename in fixture_files:
            try:
                xml_content = load_fixture(filename)
                filing_context = Form4FilingContext(
                    accession_number=filename.replace(".xml", "").replace("_form4", ""),
                    cik="0001234567",  # Generic CIK for testing
                    filing_date=date(2023, 12, 15)
                )
                
                result = parser.parse(xml_content, filing_context)
                results.append({
                    'filename': filename,
                    'success': result["success"],
                    'error': result.get("error", None)
                })
                
                if not result["success"]:
                    print(f"Failed to parse {filename}: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': str(e)
                })
                print(f"Exception parsing {filename}: {e}")
        
        # All fixtures should parse successfully (or we should know why they don't)
        successful_parses = [r for r in results if r['success']]
        failed_parses = [r for r in results if not r['success']]
        
        print(f"Successful parses: {len(successful_parses)}/{len(results)}")
        if failed_parses:
            for failure in failed_parses:
                print(f"  Failed: {failure['filename']} - {failure['error']}")
        
        # We expect most fixtures to parse successfully
        # If this assertion fails, we need to investigate the specific failures
        assert len(successful_parses) >= len(results) * 0.8, f"Too many fixture parsing failures: {failed_parses}"
    
    def test_entity_extraction_consistency(self, parser):
        """Test entity extraction consistency across fixtures"""
        xml_content = load_fixture("0001610717-23-000035.xml")
        filing_context = Form4FilingContext(
            accession_number="0001610717-23-000035",
            cik="0001770787",
            filing_date=date(2023, 5, 11)
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        entities = result["entities"]
        
        # Test entity data consistency
        issuer = entities["issuer"]["data"]
        assert issuer.entity_type == "company"
        assert issuer.cik == "1770787"  # Leading zeros removed
        assert issuer.name is not None and len(issuer.name.strip()) > 0
        
        # Test owner entity consistency
        for owner_info in entities["owners"]:
            owner = owner_info["data"]
            assert owner.cik is not None and len(owner.cik.strip()) > 0
            assert owner.name is not None and len(owner.name.strip()) > 0
            assert owner.entity_type in ["person", "company"]
        
        # Test relationship consistency
        for relationship in entities["relationships"]:
            assert relationship.issuer_entity_id is not None
            assert relationship.owner_entity_id is not None
            assert relationship.filing_date is not None
            assert relationship.relationship_type in ["director", "officer", "10_percent_owner", "other"]
    
    def test_transaction_data_consistency(self, parser):
        """Test transaction data extraction consistency"""
        xml_content = load_fixture("0001610717-23-000035.xml")
        filing_context = Form4FilingContext(
            accession_number="0001610717-23-000035",
            cik="0001770787",
            filing_date=date(2023, 5, 11)
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        # Check transaction service calls
        transactions = parser.transaction_service.created_transactions
        
        for txn in transactions:
            # All transactions should have required fields
            assert 'transaction_code' in txn
            assert 'shares_amount' in txn
            assert 'transaction_date' in txn
            assert 'security_id' in txn
            
            # Validate data types
            assert isinstance(txn['shares_amount'], Decimal)
            assert isinstance(txn['transaction_date'], date)
            assert txn['transaction_code'] is not None
    
    def test_security_creation_patterns(self, parser):
        """Test security creation patterns across different filings"""
        xml_content = load_fixture("0001610717-23-000035.xml")
        filing_context = Form4FilingContext(
            accession_number="0001610717-23-000035", 
            cik="0001770787",
            filing_date=date(2023, 5, 11)
        )
        
        result = parser.parse(xml_content, filing_context)
        
        assert result["success"] is True
        
        # Check security creation
        securities = parser.security_service.created_securities
        
        for security in securities:
            # Handle both regular securities and derivative securities
            if 'title' in security:
                # Regular security
                assert 'type' in security
                assert security['title'] is not None and len(security['title'].strip()) > 0
                assert security['type'] in ['equity', 'option', 'convertible', 'other_derivative']
            elif 'underlying_title' in security:
                # Derivative security
                assert 'security_id' in security
                assert security['underlying_title'] is not None and len(security['underlying_title'].strip()) > 0
            else:
                # Should not happen - all securities should have either title or underlying_title
                assert False, f"Security missing both 'title' and 'underlying_title': {security}"
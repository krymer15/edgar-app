# tests/forms/test_form4_writer.py
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
import sys, os
import uuid

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from models.dataclasses.entity import EntityData
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.form4_transaction import Form4TransactionData
from writers.forms.form4_writer import Form4Writer
from writers.shared.entity_writer import EntityWriter

@pytest.fixture
def sample_form4_data():
    # Create entity data objects
    issuer = EntityData(cik="0001234567", name="Test Issuer Inc", entity_type="company")
    owner = EntityData(cik="0009876543", name="Test Owner", entity_type="person")
    
    # Create relationship using entity IDs
    relationship = Form4RelationshipData(
        issuer_entity_id=issuer.id,  # Use the UUID from the EntityData object
        owner_entity_id=owner.id,    # Use the UUID from the EntityData object
        filing_date=date(2025, 5, 15),
        is_director=True,
        is_officer=True,
        is_ten_percent_owner=False,
        is_other=False,
        officer_title="CEO",
        other_text=None,
        relationship_type="officer",
        total_shares_owned=None  # Bug 11 Fix: Include total_shares_owned field
    )
    
    # Create a regular transaction
    transaction = Form4TransactionData(
        security_title="Common Stock",
        transaction_date=date(2025, 5, 14),
        transaction_code="P",
        shares_amount=1000,
        price_per_share=15.50,
        ownership_nature="D",
        acquisition_disposition_flag="A",  # Add A/D flag
        is_position_only=False  # Bug 10 Fix: Set is_position_only field
    )
    
    # Create a position-only row
    position = Form4TransactionData(
        security_title="Preferred Stock",
        transaction_code="H",  # "H" for holdings
        shares_amount=500,
        ownership_nature="D",
        is_position_only=True,  # Bug 10 Fix: Mark as position-only
        transaction_date=None   # Position-only rows have no transaction date
    )
    
    filing = Form4FilingData(
        accession_number="0001234567-25-000001",
        period_of_report=date(2025, 5, 14),
        relationships=[relationship],
        transactions=[transaction, position]  # Include both transaction and position
    )
    
    # We also need to store the entity objects for the test to use
    # Add them as attributes to the filing object with the new naming convention
    filing.issuer_entity = issuer
    
    # For owner_entities, we now use a list
    filing.owner_entities = [owner]
    
    return filing

def test_entity_writer_get_or_create_entity():
    mock_session = MagicMock()
    entity_data = EntityData(cik="0001234567", name="Test Entity", entity_type="company")
    
    # Mock existing entity
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    mock_existing = MagicMock()
    mock_existing.name = entity_data.name
    mock_filter.first.return_value = mock_existing
    
    writer = EntityWriter(db_session=mock_session)
    result = writer.get_or_create_entity(entity_data)
    
    mock_session.query.assert_called_once()
    # Check that filter was called with the correct arguments
    mock_query.filter.assert_called_once()
    assert result == mock_existing

def test_form4_writer_write_form4_data(sample_form4_data):
    mock_session = MagicMock()
    
    # Mock existing filing check
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter_by.return_value = mock_filter
    mock_filter.first.return_value = None  # No existing filing
    
    # Create a dummy Form4Filing class to mock the real one and avoid relationship issues
    class MockForm4Filing:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            self.accession_number = kwargs.get('accession_number')
            self.period_of_report = kwargs.get('period_of_report')
            self.has_multiple_owners = kwargs.get('has_multiple_owners', False)
            
    # Create a patch for the Form4Filing class
    with patch('writers.forms.form4_writer.Form4Filing', MockForm4Filing):
        # Mock entity writer
        mock_entity_writer = MagicMock()
        
        # Mock entities - we need these for both the issuer and owner
        mock_issuer_entity = MagicMock()
        mock_issuer_entity.id = "issuer-uuid"
        mock_owner_entity = MagicMock()
        mock_owner_entity.id = "owner-uuid"
        
        # Set up return values for get_or_create_entity with direct entity objects
        mock_entity_writer.get_or_create_entity.side_effect = [mock_issuer_entity, mock_owner_entity]
        
        # For entity lookups by ID or CIK
        mock_entity_writer.get_entity_by_id.side_effect = [mock_issuer_entity, mock_owner_entity]
        mock_entity_writer.get_entity_by_cik.side_effect = [mock_issuer_entity, mock_owner_entity]
        
        # Create a patch for the Form4Relationship class
        class MockForm4Relationship:
            def __init__(self, **kwargs):
                self.id = str(uuid.uuid4())
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Create a patch for the Form4Transaction class
        class MockForm4Transaction:
            def __init__(self, **kwargs):
                self.id = str(uuid.uuid4())
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Apply all our patches
        with patch('writers.forms.form4_writer.EntityWriter', return_value=mock_entity_writer):
            with patch('writers.forms.form4_writer.Form4Relationship', MockForm4Relationship):
                with patch('writers.forms.form4_writer.Form4Transaction', MockForm4Transaction):
                    writer = Form4Writer(db_session=mock_session)
                    result = writer.write_form4_data(sample_form4_data)
                    
                    # Check that we received a valid result
                    assert result is not None, "Expected a Form4Filing object result"
                    assert isinstance(result, MockForm4Filing), "Expected result to be a Form4Filing object"
                    
                    # Check that we added objects to the session
                    # We should have at least one add call for the new filing
                    add_calls = mock_session.add.call_count
                    assert add_calls >= 1, f"Expected at least 1 session.add call, but got {add_calls}"
                    
                    # Verify commit was called
                    # We now expect five commit calls with our implementation:
                    # 1. After entity creation
                    # 2. Before creating relationships (to ensure entities are in DB)
                    # 3. After creating transactions
                    # 4. After transaction processing (additional commit we added)
                    # 5. Final commit for all changes
                    assert mock_session.commit.call_count == 5
                    
                    # Check that entity writer methods were called
                    # With our new implementation, we expect two entities to be processed
                    # one for issuer and one for owner
                    assert mock_entity_writer.get_or_create_entity.call_count >= 1

def test_form4_writer_handles_existing_filing(sample_form4_data):
    mock_session = MagicMock()
    
    # Create dummy classes to mock the ORM models
    class MockForm4Filing:
        def __init__(self, **kwargs):
            self.id = "existing-filing-id"
            self.accession_number = kwargs.get('accession_number')
            self.period_of_report = None
            self.has_multiple_owners = None
    
    # Create an existing filing instance
    mock_existing = MockForm4Filing(accession_number=sample_form4_data.accession_number)
    
    # Set up the first query to find the filing by accession number
    mock_filing_query = MagicMock()
    mock_filing_filter = MagicMock()
    mock_filing_filter.first.return_value = mock_existing
    mock_filing_query.filter_by.return_value = mock_filing_filter
    
    # Mock transaction and relationship queries for deletion
    mock_transaction_query = MagicMock()
    mock_transaction_filter = MagicMock()
    mock_transaction_query.filter_by.return_value = mock_transaction_filter
    
    mock_relationship_query = MagicMock()
    mock_relationship_filter = MagicMock()
    mock_relationship_query.filter_by.return_value = mock_relationship_filter
    
    # Mock query for calculating total_shares_owned
    mock_rel_id_query = MagicMock()
    mock_rel_id_filter = MagicMock()
    mock_rel_id_query.filter_by.return_value = mock_rel_id_filter
    mock_rel_id_all = []
    mock_rel_id_filter.all.return_value = mock_rel_id_all
    
    # We need to mock four different query calls
    mock_session.query.side_effect = [
        mock_filing_query,        # First call to find existing filing
        mock_transaction_query,   # Second call to delete transactions
        mock_relationship_query,  # Third call to delete relationships
        mock_rel_id_query         # Fourth call to get relationships for total_shares_owned
    ]
    
    # Create mocks for the relationship and transaction classes
    class MockForm4Relationship:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            self.total_shares_owned = None  # Add field for total_shares_owned
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MockForm4Transaction:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            self.is_position_only = False  # Add field for is_position_only
            self.transaction_date = kwargs.get('transaction_date')
            self.shares_amount = kwargs.get('shares_amount')
            self.acquisition_disposition_flag = kwargs.get('acquisition_disposition_flag')
            for key, value in kwargs.items():
                setattr(self, key, value)
                
        # Add property to match the dataclass
        @property
        def position_value(self):
            if self.shares_amount is None:
                return None
            if getattr(self, 'is_position_only', False):
                return self.shares_amount
            if getattr(self, 'acquisition_disposition_flag', None) == 'A':
                return self.shares_amount
            elif getattr(self, 'acquisition_disposition_flag', None) == 'D':
                return -self.shares_amount
            return self.shares_amount
    
    # Set up mock for entity writer
    mock_entity_writer = MagicMock()
    mock_issuer_entity = MagicMock()
    mock_owner_entity = MagicMock()
    mock_entity_writer.get_or_create_entity.side_effect = [mock_issuer_entity, mock_owner_entity]
    mock_entity_writer.get_entity_by_id.side_effect = [mock_issuer_entity, mock_owner_entity]
    mock_entity_writer.get_entity_by_cik.side_effect = [mock_issuer_entity, mock_owner_entity]
    
    # Apply our patches
    with patch('writers.forms.form4_writer.Form4Filing', MockForm4Filing):
        with patch('writers.forms.form4_writer.Form4Relationship', MockForm4Relationship):
            with patch('writers.forms.form4_writer.Form4Transaction', MockForm4Transaction):
                with patch('writers.forms.form4_writer.EntityWriter', return_value=mock_entity_writer):
                    # Import decimal for the test
                    from decimal import Decimal
                    
                    writer = Form4Writer(db_session=mock_session)
                    result = writer.write_form4_data(sample_form4_data)
                    
                    # Check that the result is the existing filing
                    assert result == mock_existing
                    
                    # Verify that the existing data was updated
                    assert mock_existing.period_of_report == sample_form4_data.period_of_report
                    assert mock_existing.has_multiple_owners == sample_form4_data.has_multiple_owners
                    
                    # Verify that existing transactions and relationships were deleted
                    mock_transaction_filter.delete.assert_called_once()
                    mock_relationship_filter.delete.assert_called_once()
                    
                    # Verify that commit was called
                    # Note: Exact commit count may vary based on implementation
                    assert mock_session.commit.call_count >= 3, f"Expected at least 3 commits, got {mock_session.commit.call_count}"

def test_form4_writer_handles_database_error(sample_form4_data):
    """Test that the writer properly handles database errors"""
    mock_session = MagicMock()
    
    # Create dummy classes for our models
    class MockForm4Filing:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MockForm4Relationship:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MockForm4Transaction:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # Mock query for existing filing check
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter_by.return_value = mock_filter
    mock_filter.first.return_value = None  # No existing filing
    
    # Set up entity writer mocks
    mock_entity_writer = MagicMock()
    
    # Setup the session to raise an exception when flush is called
    from sqlalchemy.exc import SQLAlchemyError
    mock_session.flush.side_effect = SQLAlchemyError("Database error")
    
    # Apply our patches
    with patch('writers.forms.form4_writer.Form4Filing', MockForm4Filing):
        with patch('writers.forms.form4_writer.Form4Relationship', MockForm4Relationship):
            with patch('writers.forms.form4_writer.Form4Transaction', MockForm4Transaction):
                with patch('writers.forms.form4_writer.EntityWriter', return_value=mock_entity_writer):
                    writer = Form4Writer(db_session=mock_session)
                    result = writer.write_form4_data(sample_form4_data)
                    
                    # Check that we got None result due to error
                    assert result is None
                    
                    # Verify that rollback was called
                    # Our implementation now calls rollback at the start and when an error occurs
                    assert mock_session.rollback.call_count == 2
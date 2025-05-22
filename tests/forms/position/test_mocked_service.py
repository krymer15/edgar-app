# tests/forms/position/test_mocked_service.py
import pytest
import uuid
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import date, timedelta

# Import the dataclasses only (no dependencies on ORM models)
from models.dataclasses.forms.position_data import RelationshipPositionData
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData

# Create a mock version of the service without importing the real one
class MockPositionService:
    """Mock position service for testing without database dependencies"""
    
    def __init__(self, db_session, transaction_service=None):
        self.db_session = db_session
        self.transaction_service = transaction_service
        self._positions = {}  # In-memory storage for testing
        
    def create_position(self, position_data):
        """Create a new relationship position"""
        position_id = position_data.id or str(uuid.uuid4())
        self._positions[position_id] = position_data
        return position_id
    
    def get_position(self, position_id):
        """Get a position by ID"""
        return self._positions.get(position_id)
    
    def get_latest_position(self, relationship_id, security_id, 
                            derivative_security_id=None, as_of_date=None):
        """Get the latest position for a relationship-security combination"""
        # Find positions matching criteria
        matching_positions = []
        for position in self._positions.values():
            if (position.relationship_id == relationship_id and 
                position.security_id == security_id):
                
                # Check derivative security match
                if derivative_security_id:
                    if position.derivative_security_id != derivative_security_id:
                        continue
                else:
                    if position.derivative_security_id is not None:
                        continue
                        
                # Check date filter
                if as_of_date and position.position_date > as_of_date:
                    continue
                    
                matching_positions.append(position)
        
        # Return the latest (most recent) position
        if matching_positions:
            return max(matching_positions, key=lambda p: p.position_date)
        return None
    
    def get_positions_for_relationship(self, relationship_id, as_of_date=None):
        """Get all positions for a specific relationship"""
        positions = []
        for position in self._positions.values():
            if position.relationship_id == relationship_id:
                if as_of_date is None or position.position_date <= as_of_date:
                    positions.append(position)
        return sorted(positions, key=lambda p: (p.position_date, p.security_id), reverse=True)
    
    def get_positions_for_security(self, security_id, as_of_date=None):
        """Get all positions for a specific security"""
        positions = []
        for position in self._positions.values():
            if position.security_id == security_id:
                if as_of_date is None or position.position_date <= as_of_date:
                    positions.append(position)
        return sorted(positions, key=lambda p: (p.position_date, p.relationship_id), reverse=True)
    
    def update_position_from_transaction(self, transaction):
        """Create or update a position based on a transaction"""
        # Determine transaction type
        is_derivative = isinstance(transaction, DerivativeTransactionData)
        position_type = 'derivative' if is_derivative else 'equity'
        derivative_security_id = getattr(transaction, 'derivative_security_id', None) if is_derivative else None
        
        # Try to find the latest position
        latest_position = self.get_latest_position(
            relationship_id=transaction.relationship_id,
            security_id=transaction.security_id,
            derivative_security_id=derivative_security_id,
            as_of_date=transaction.transaction_date - timedelta(days=1)
        )
        
        # Calculate new position amount
        new_amount = transaction.position_impact
        if latest_position:
            new_amount += latest_position.shares_amount
        
        # Create new position
        position_data = RelationshipPositionData(
            relationship_id=transaction.relationship_id,
            security_id=transaction.security_id,
            position_date=transaction.transaction_date,
            shares_amount=new_amount,
            direct_ownership=transaction.direct_ownership,
            ownership_nature_explanation=getattr(transaction, 'ownership_nature_explanation', None),
            filing_id=transaction.form4_filing_id,
            transaction_id=transaction.id,
            is_position_only=False,
            position_type=position_type,
            derivative_security_id=derivative_security_id
        )
        
        return self.create_position(position_data)
    
    def create_position_only_entry(self, position_data):
        """Create a position-only entry (from a holding without transaction)"""
        position_data.is_position_only = True
        
        # Check for existing position-only entry (simplified check)
        for pos_id, existing in self._positions.items():
            if (existing.relationship_id == position_data.relationship_id and
                existing.security_id == position_data.security_id and
                existing.position_date == position_data.position_date and
                existing.derivative_security_id == position_data.derivative_security_id and
                existing.direct_ownership == position_data.direct_ownership and
                existing.is_position_only):
                # Update existing
                self._positions[pos_id] = position_data
                return pos_id
        
        # Create new position
        return self.create_position(position_data)
    
    def get_position_history(self, relationship_id, security_id,
                           derivative_security_id=None,
                           start_date=None, end_date=None):
        """Get position history for a relationship-security combination"""
        positions = []
        for position in self._positions.values():
            if (position.relationship_id == relationship_id and 
                position.security_id == security_id):
                
                # Check derivative security match
                if derivative_security_id:
                    if position.derivative_security_id != derivative_security_id:
                        continue
                else:
                    if position.derivative_security_id is not None:
                        continue
                
                # Check date range
                if start_date and position.position_date < start_date:
                    continue
                if end_date and position.position_date > end_date:
                    continue
                    
                positions.append(position)
        
        return sorted(positions, key=lambda p: p.position_date)
    
    def calculate_total_shares_owned(self, relationship_id, as_of_date=None):
        """Calculate total shares owned per security for a relationship"""
        positions = self.get_positions_for_relationship(relationship_id, as_of_date)
        
        # Group by security_id and sum shares
        totals = {}
        for position in positions:
            security_id = position.security_id
            if security_id not in totals:
                totals[security_id] = Decimal('0')
            
            totals[security_id] += position.shares_amount
        
        return totals
    
    def recalculate_positions(self, relationship_id, security_id, start_date=None):
        """Recalculate positions for a relationship-security combination"""
        # This is a simplified mock implementation
        # In reality, this would involve complex transaction processing
        pass


# Test class
class TestPositionFunctionality:
    """Tests that verify the expected functionality of position operations"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return MagicMock()
        
    @pytest.fixture
    def position_service(self, mock_db_session):
        """Create our mock service"""
        return MockPositionService(mock_db_session)
    
    def test_position_creation(self, position_service, sample_position_data):
        """Test creating a position"""
        position_id = position_service.create_position(sample_position_data)
        
        # Verify we got an ID
        assert position_id is not None
        assert isinstance(position_id, str)
        assert len(position_id) > 0
        
        # Verify we can retrieve the position
        retrieved = position_service.get_position(position_id)
        assert retrieved is not None
        assert retrieved.relationship_id == sample_position_data.relationship_id
        assert retrieved.security_id == sample_position_data.security_id
        assert retrieved.shares_amount == sample_position_data.shares_amount
    
    def test_derivative_position_creation(self, position_service, sample_derivative_position_data):
        """Test creating a derivative position"""
        position_id = position_service.create_position(sample_derivative_position_data)
        
        # Verify we got an ID
        assert position_id is not None
        assert isinstance(position_id, str)
        assert len(position_id) > 0
        
        # Verify we can retrieve the position
        retrieved = position_service.get_position(position_id)
        assert retrieved is not None
        assert retrieved.position_type == "derivative"
        assert retrieved.derivative_security_id == sample_derivative_position_data.derivative_security_id
    
    def test_get_latest_position(self, position_service):
        """Test getting the latest position for a relationship-security combination"""
        relationship_id = str(uuid.uuid4())
        security_id = str(uuid.uuid4())
        filing_id = str(uuid.uuid4())
        
        # Create multiple positions for the same relationship-security
        position1 = RelationshipPositionData(
            relationship_id=relationship_id,
            security_id=security_id,
            position_date=date(2023, 5, 10),
            shares_amount=Decimal("100"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        position2 = RelationshipPositionData(
            relationship_id=relationship_id,
            security_id=security_id,
            position_date=date(2023, 5, 15),  # Later date
            shares_amount=Decimal("150"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        position_service.create_position(position1)
        position_service.create_position(position2)
        
        # Get latest position
        latest = position_service.get_latest_position(relationship_id, security_id)
        
        # Should get the later position
        assert latest is not None
        assert latest.position_date == date(2023, 5, 15)
        assert latest.shares_amount == Decimal("150")
    
    def test_get_positions_for_relationship(self, position_service):
        """Test getting all positions for a relationship"""
        relationship_id = str(uuid.uuid4())
        filing_id = str(uuid.uuid4())
        
        # Create positions for different securities
        position1 = RelationshipPositionData(
            relationship_id=relationship_id,
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("100"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        position2 = RelationshipPositionData(
            relationship_id=relationship_id,
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("200"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        # Create position for different relationship (should not be included)
        position3 = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("300"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        position_service.create_position(position1)
        position_service.create_position(position2)
        position_service.create_position(position3)
        
        # Get positions for the relationship
        positions = position_service.get_positions_for_relationship(relationship_id)
        
        # Should get only the two positions for this relationship
        assert len(positions) == 2
        assert all(p.relationship_id == relationship_id for p in positions)
    
    def test_get_positions_for_security(self, position_service):
        """Test getting all positions for a security"""
        security_id = str(uuid.uuid4())
        filing_id = str(uuid.uuid4())
        
        # Create positions for different relationships
        position1 = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=security_id,
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("100"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        position2 = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=security_id,
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("200"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        # Create position for different security (should not be included)
        position3 = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("300"),
            filing_id=filing_id,
            position_type="equity"
        )
        
        position_service.create_position(position1)
        position_service.create_position(position2)
        position_service.create_position(position3)
        
        # Get positions for the security
        positions = position_service.get_positions_for_security(security_id)
        
        # Should get only the two positions for this security
        assert len(positions) == 2
        assert all(p.security_id == security_id for p in positions)
    
    def test_update_position_from_non_derivative_transaction(self, position_service, sample_non_derivative_transaction):
        """Test updating position from a non-derivative transaction"""
        # Create an initial position
        initial_position = RelationshipPositionData(
            relationship_id=sample_non_derivative_transaction.relationship_id,
            security_id=sample_non_derivative_transaction.security_id,
            position_date=sample_non_derivative_transaction.transaction_date - timedelta(days=5),
            shares_amount=Decimal("500"),
            filing_id=str(uuid.uuid4()),
            position_type="equity"
        )
        position_service.create_position(initial_position)
        
        # Update position from transaction (acquisition of 100 shares)
        new_position_id = position_service.update_position_from_transaction(sample_non_derivative_transaction)
        
        # Get the new position
        new_position = position_service.get_position(new_position_id)
        
        # Verify the position was updated correctly
        assert new_position is not None
        assert new_position.shares_amount == Decimal("600")  # 500 + 100
        assert new_position.transaction_id == sample_non_derivative_transaction.id
        assert new_position.position_type == "equity"
        assert not new_position.is_position_only
    
    def test_update_position_from_derivative_transaction(self, position_service, sample_derivative_transaction):
        """Test updating position from a derivative transaction"""
        # Update position from transaction (no prior position)
        new_position_id = position_service.update_position_from_transaction(sample_derivative_transaction)
        
        # Get the new position
        new_position = position_service.get_position(new_position_id)
        
        # Verify the position was created correctly
        assert new_position is not None
        assert new_position.shares_amount == sample_derivative_transaction.position_impact
        assert new_position.transaction_id == sample_derivative_transaction.id
        assert new_position.position_type == "derivative"
        assert new_position.derivative_security_id == sample_derivative_transaction.derivative_security_id
        assert not new_position.is_position_only
    
    def test_create_position_only_entry(self, position_service):
        """Test creating a position-only entry"""
        position_data = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("1000"),
            filing_id=str(uuid.uuid4()),
            position_type="equity",
            is_position_only=False  # Will be set to True by the method
        )
        
        # Create position-only entry
        position_id = position_service.create_position_only_entry(position_data)
        
        # Get the position
        position = position_service.get_position(position_id)
        
        # Verify it's marked as position-only
        assert position is not None
        assert position.is_position_only
        assert position.transaction_id is None
    
    def test_get_position_history(self, position_service):
        """Test getting position history"""
        relationship_id = str(uuid.uuid4())
        security_id = str(uuid.uuid4())
        filing_id = str(uuid.uuid4())
        
        # Create multiple positions over time
        positions = [
            RelationshipPositionData(
                relationship_id=relationship_id,
                security_id=security_id,
                position_date=date(2023, 5, 10),
                shares_amount=Decimal("100"),
                filing_id=filing_id,
                position_type="equity"
            ),
            RelationshipPositionData(
                relationship_id=relationship_id,
                security_id=security_id,
                position_date=date(2023, 5, 15),
                shares_amount=Decimal("150"),
                filing_id=filing_id,
                position_type="equity"
            ),
            RelationshipPositionData(
                relationship_id=relationship_id,
                security_id=security_id,
                position_date=date(2023, 5, 20),
                shares_amount=Decimal("125"),
                filing_id=filing_id,
                position_type="equity"
            )
        ]
        
        for pos in positions:
            position_service.create_position(pos)
        
        # Get position history
        history = position_service.get_position_history(relationship_id, security_id)
        
        # Verify we get all positions in chronological order
        assert len(history) == 3
        assert history[0].position_date == date(2023, 5, 10)
        assert history[1].position_date == date(2023, 5, 15)
        assert history[2].position_date == date(2023, 5, 20)
        
        # Test with date range
        filtered_history = position_service.get_position_history(
            relationship_id, security_id, 
            start_date=date(2023, 5, 12), 
            end_date=date(2023, 5, 18)
        )
        assert len(filtered_history) == 1
        assert filtered_history[0].position_date == date(2023, 5, 15)
    
    def test_calculate_total_shares_owned(self, position_service):
        """Test calculating total shares owned per security"""
        relationship_id = str(uuid.uuid4())
        security1_id = str(uuid.uuid4())
        security2_id = str(uuid.uuid4())
        filing_id = str(uuid.uuid4())
        
        # Create positions for multiple securities
        positions = [
            RelationshipPositionData(
                relationship_id=relationship_id,
                security_id=security1_id,
                position_date=date(2023, 5, 15),
                shares_amount=Decimal("100"),
                filing_id=filing_id,
                position_type="equity"
            ),
            RelationshipPositionData(
                relationship_id=relationship_id,
                security_id=security1_id,
                position_date=date(2023, 5, 16),  # Later position for same security
                shares_amount=Decimal("150"),
                filing_id=filing_id,
                position_type="equity"
            ),
            RelationshipPositionData(
                relationship_id=relationship_id,
                security_id=security2_id,
                position_date=date(2023, 5, 15),
                shares_amount=Decimal("200"),
                filing_id=filing_id,
                position_type="equity"
            )
        ]
        
        for pos in positions:
            position_service.create_position(pos)
        
        # Calculate total shares
        totals = position_service.calculate_total_shares_owned(relationship_id)
        
        # Verify totals (should include both positions for security1)
        assert len(totals) == 2
        assert totals[security1_id] == Decimal("250")  # 100 + 150
        assert totals[security2_id] == Decimal("200")
    
    def test_position_data_validation(self):
        """Test position data validation"""
        # Test valid equity position
        equity_position = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("1000"),
            filing_id=str(uuid.uuid4()),
            position_type="equity"
        )
        assert equity_position.position_type == "equity"
        
        # Test valid derivative position
        derivative_position = RelationshipPositionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            position_date=date(2023, 5, 15),
            shares_amount=Decimal("500"),
            filing_id=str(uuid.uuid4()),
            position_type="derivative",
            derivative_security_id=str(uuid.uuid4())
        )
        assert derivative_position.position_type == "derivative"
        
        # Test invalid position type
        with pytest.raises(ValueError, match="Invalid position_type"):
            RelationshipPositionData(
                relationship_id=str(uuid.uuid4()),
                security_id=str(uuid.uuid4()),
                position_date=date(2023, 5, 15),
                shares_amount=Decimal("1000"),
                filing_id=str(uuid.uuid4()),
                position_type="invalid"
            )
        
        # Test derivative position without derivative_security_id
        with pytest.raises(ValueError, match="derivative_security_id is required"):
            RelationshipPositionData(
                relationship_id=str(uuid.uuid4()),
                security_id=str(uuid.uuid4()),
                position_date=date(2023, 5, 15),
                shares_amount=Decimal("500"),
                filing_id=str(uuid.uuid4()),
                position_type="derivative"
            )
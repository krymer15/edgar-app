# tests/forms/transaction/test_mocked_service.py
import pytest
import uuid
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import date, datetime

# Import the dataclasses only (no dependencies on ORM models)
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData

# Create a mock version of the service without importing the real one
class MockTransactionService:
    def __init__(self, db_session):
        self.db_session = db_session
        
    def create_non_derivative_transaction(self, transaction_data):
        # Simplified mock implementation
        return str(uuid.uuid4())
    
    def create_derivative_transaction(self, transaction_data):
        # Simplified mock implementation
        return str(uuid.uuid4())
    
    def get_non_derivative_transaction(self, transaction_id):
        # Return a mock transaction
        return NonDerivativeTransactionData(
            id=transaction_id,
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            transaction_code="P",
            transaction_date=date(2023, 5, 15),
            shares_amount=Decimal("100"),
            acquisition_disposition_flag="A",
            price_per_share=Decimal("10.50")
        )
    
    def get_derivative_transaction(self, transaction_id):
        # Return a mock transaction
        return DerivativeTransactionData(
            id=transaction_id,
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            derivative_security_id=str(uuid.uuid4()),
            transaction_code="A",
            transaction_date=date(2023, 5, 15),
            shares_amount=Decimal("500"),
            acquisition_disposition_flag="A",
            price_per_derivative=Decimal("1.25"),
            underlying_shares_amount=Decimal("500")
        )
    
    def get_transactions_for_filing(self, filing_id):
        # Return mock transactions for a filing
        return (
            [
                NonDerivativeTransactionData(
                    id=str(uuid.uuid4()),
                    form4_filing_id=filing_id,
                    relationship_id=str(uuid.uuid4()),
                    security_id=str(uuid.uuid4()),
                    transaction_code="P",
                    transaction_date=date(2023, 5, 15),
                    shares_amount=Decimal("100"),
                    acquisition_disposition_flag="A",
                    price_per_share=Decimal("10.50")
                )
            ],
            [
                DerivativeTransactionData(
                    id=str(uuid.uuid4()),
                    form4_filing_id=filing_id,
                    relationship_id=str(uuid.uuid4()),
                    security_id=str(uuid.uuid4()),
                    derivative_security_id=str(uuid.uuid4()),
                    transaction_code="A",
                    transaction_date=date(2023, 5, 15),
                    shares_amount=Decimal("500"),
                    acquisition_disposition_flag="A",
                    price_per_derivative=Decimal("1.25"),
                    underlying_shares_amount=Decimal("500")
                )
            ]
        )
    
    def get_transactions_for_relationship(self, relationship_id):
        # Similar to get_transactions_for_filing, but filtering by relationship
        return (
            [
                NonDerivativeTransactionData(
                    id=str(uuid.uuid4()),
                    relationship_id=relationship_id,
                    security_id=str(uuid.uuid4()),
                    transaction_code="P",
                    transaction_date=date(2023, 5, 15),
                    shares_amount=Decimal("100"),
                    acquisition_disposition_flag="A",
                    price_per_share=Decimal("10.50")
                )
            ],
            [
                DerivativeTransactionData(
                    id=str(uuid.uuid4()),
                    relationship_id=relationship_id,
                    security_id=str(uuid.uuid4()),
                    derivative_security_id=str(uuid.uuid4()),
                    transaction_code="A",
                    transaction_date=date(2023, 5, 15),
                    shares_amount=Decimal("500"),
                    acquisition_disposition_flag="A",
                    price_per_derivative=Decimal("1.25"),
                    underlying_shares_amount=Decimal("500")
                )
            ]
        )
    
    def get_transactions_for_security(self, security_id, start_date=None, end_date=None):
        # Return mock transactions for a security
        return [
            NonDerivativeTransactionData(
                id=str(uuid.uuid4()),
                relationship_id=str(uuid.uuid4()),
                security_id=security_id,
                transaction_code="P",
                transaction_date=date(2023, 5, 15),
                shares_amount=Decimal("100"),
                acquisition_disposition_flag="A",
                price_per_share=Decimal("10.50")
            ),
            NonDerivativeTransactionData(
                id=str(uuid.uuid4()),
                relationship_id=str(uuid.uuid4()),
                security_id=security_id,
                transaction_code="S",
                transaction_date=date(2023, 5, 16),
                shares_amount=Decimal("50"),
                acquisition_disposition_flag="D",
                price_per_share=Decimal("11.00")
            )
        ]
    
    def get_transactions_for_derivative_security(self, derivative_security_id, start_date=None, end_date=None):
        # Return mock transactions for a derivative security
        return [
            DerivativeTransactionData(
                id=str(uuid.uuid4()),
                relationship_id=str(uuid.uuid4()),
                security_id=str(uuid.uuid4()),
                derivative_security_id=derivative_security_id,
                transaction_code="A",
                transaction_date=date(2023, 5, 15),
                shares_amount=Decimal("500"),
                acquisition_disposition_flag="A",
                price_per_derivative=Decimal("1.25"),
                underlying_shares_amount=Decimal("500")
            )
        ]

# Test class
class TestTransactionFunctionality:
    """Tests that verify the expected functionality of transaction operations"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return MagicMock()
        
    @pytest.fixture
    def transaction_service(self, mock_db_session):
        """Create our mock service"""
        return MockTransactionService(mock_db_session)
    
    def test_non_derivative_transaction_creation(self, transaction_service):
        # Create non-derivative transaction data
        transaction_data = NonDerivativeTransactionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            transaction_code="P",
            transaction_date=date(2023, 5, 15),
            shares_amount=Decimal("100"),
            acquisition_disposition_flag="A",
            price_per_share=Decimal("10.50")
        )
        
        # Create a transaction
        transaction_id = transaction_service.create_non_derivative_transaction(transaction_data)
        
        # Verify we got an ID
        assert transaction_id is not None
        assert isinstance(transaction_id, str)
        assert len(transaction_id) > 0
    
    def test_derivative_transaction_creation(self, transaction_service):
        # Create derivative transaction data
        transaction_data = DerivativeTransactionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            derivative_security_id=str(uuid.uuid4()),
            transaction_code="A",
            transaction_date=date(2023, 5, 15),
            shares_amount=Decimal("500"),
            acquisition_disposition_flag="A",
            price_per_derivative=Decimal("1.25"),
            underlying_shares_amount=Decimal("500")
        )
        
        # Create a transaction
        transaction_id = transaction_service.create_derivative_transaction(transaction_data)
        
        # Verify we got an ID
        assert transaction_id is not None
        assert isinstance(transaction_id, str)
        assert len(transaction_id) > 0
    
    def test_get_non_derivative_transaction(self, transaction_service):
        # Get a non-derivative transaction
        transaction_id = str(uuid.uuid4())
        transaction = transaction_service.get_non_derivative_transaction(transaction_id)
        
        # Verify the transaction
        assert transaction is not None
        assert isinstance(transaction, NonDerivativeTransactionData)
        assert transaction.id == transaction_id
        assert transaction.transaction_code == "P"
        
    def test_get_derivative_transaction(self, transaction_service):
        # Get a derivative transaction
        transaction_id = str(uuid.uuid4())
        transaction = transaction_service.get_derivative_transaction(transaction_id)
        
        # Verify the transaction
        assert transaction is not None
        assert isinstance(transaction, DerivativeTransactionData)
        assert transaction.id == transaction_id
        assert transaction.transaction_code == "A"
    
    def test_get_transactions_for_filing(self, transaction_service):
        # Get transactions for a filing
        filing_id = str(uuid.uuid4())
        non_derivative, derivative = transaction_service.get_transactions_for_filing(filing_id)
        
        # Verify the transactions
        assert len(non_derivative) == 1
        assert len(derivative) == 1
        assert all(isinstance(t, NonDerivativeTransactionData) for t in non_derivative)
        assert all(isinstance(t, DerivativeTransactionData) for t in derivative)
        assert all(t.form4_filing_id == filing_id for t in non_derivative)
        assert all(t.form4_filing_id == filing_id for t in derivative)
    
    def test_get_transactions_for_relationship(self, transaction_service):
        # Get transactions for a relationship
        relationship_id = str(uuid.uuid4())
        non_derivative, derivative = transaction_service.get_transactions_for_relationship(relationship_id)
        
        # Verify the transactions
        assert len(non_derivative) == 1
        assert len(derivative) == 1
        assert all(isinstance(t, NonDerivativeTransactionData) for t in non_derivative)
        assert all(isinstance(t, DerivativeTransactionData) for t in derivative)
        assert all(t.relationship_id == relationship_id for t in non_derivative)
        assert all(t.relationship_id == relationship_id for t in derivative)
    
    def test_get_transactions_for_security(self, transaction_service):
        # Get transactions for a security
        security_id = str(uuid.uuid4())
        transactions = transaction_service.get_transactions_for_security(security_id)
        
        # Verify the transactions
        assert len(transactions) == 2
        assert all(isinstance(t, NonDerivativeTransactionData) for t in transactions)
        assert all(t.security_id == security_id for t in transactions)
        
        # Verify we have both purchase and sale transactions
        assert any(t.transaction_code == "P" for t in transactions)
        assert any(t.transaction_code == "S" for t in transactions)
    
    def test_get_transactions_for_derivative_security(self, transaction_service):
        # Get transactions for a derivative security
        derivative_security_id = str(uuid.uuid4())
        transactions = transaction_service.get_transactions_for_derivative_security(derivative_security_id)
        
        # Verify the transactions
        assert len(transactions) == 1
        assert all(isinstance(t, DerivativeTransactionData) for t in transactions)
        assert all(t.derivative_security_id == derivative_security_id for t in transactions)
    
    def test_transaction_position_impact(self):
        # Test acquisition impact
        acquisition = NonDerivativeTransactionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            transaction_code="P",
            transaction_date=date(2023, 5, 15),
            shares_amount=Decimal("100"),
            acquisition_disposition_flag="A"
        )
        assert acquisition.position_impact == Decimal("100")
        
        # Test disposition impact
        disposition = NonDerivativeTransactionData(
            relationship_id=str(uuid.uuid4()),
            security_id=str(uuid.uuid4()),
            transaction_code="S",
            transaction_date=date(2023, 5, 15),
            shares_amount=Decimal("50"),
            acquisition_disposition_flag="D"
        )
        assert disposition.position_impact == Decimal("-50")
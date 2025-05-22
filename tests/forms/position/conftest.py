# tests/forms/position/conftest.py
import pytest
import uuid
from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date

# Import the dataclass only (no dependencies on ORM models)
from models.dataclasses.forms.position_data import RelationshipPositionData
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData

@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return MagicMock()

@pytest.fixture
def sample_position_data():
    """Create sample position data for testing"""
    return RelationshipPositionData(
        relationship_id=str(uuid.uuid4()),
        security_id=str(uuid.uuid4()),
        position_date=date(2023, 5, 15),
        shares_amount=Decimal("1000"),
        filing_id=str(uuid.uuid4()),
        position_type="equity",
        direct_ownership=True,
        ownership_nature_explanation="Direct ownership",
        is_position_only=False
    )

@pytest.fixture
def sample_derivative_position_data():
    """Create sample derivative position data for testing"""
    return RelationshipPositionData(
        relationship_id=str(uuid.uuid4()),
        security_id=str(uuid.uuid4()),
        position_date=date(2023, 5, 15),
        shares_amount=Decimal("500"),
        filing_id=str(uuid.uuid4()),
        position_type="derivative",
        derivative_security_id=str(uuid.uuid4()),
        direct_ownership=True,
        is_position_only=False
    )

@pytest.fixture
def sample_non_derivative_transaction():
    """Create sample non-derivative transaction for testing"""
    return NonDerivativeTransactionData(
        relationship_id=str(uuid.uuid4()),
        security_id=str(uuid.uuid4()),
        transaction_code="P",
        transaction_date=date(2023, 5, 15),
        shares_amount=Decimal("100"),
        acquisition_disposition_flag="A",
        price_per_share=Decimal("10.50"),
        form4_filing_id=str(uuid.uuid4()),
        direct_ownership=True
    )

@pytest.fixture
def sample_derivative_transaction():
    """Create sample derivative transaction for testing"""
    return DerivativeTransactionData(
        relationship_id=str(uuid.uuid4()),
        security_id=str(uuid.uuid4()),
        derivative_security_id=str(uuid.uuid4()),
        transaction_code="A",
        transaction_date=date(2023, 5, 15),
        shares_amount=Decimal("500"),
        acquisition_disposition_flag="A",
        price_per_derivative=Decimal("1.25"),
        underlying_shares_amount=Decimal("500"),
        form4_filing_id=str(uuid.uuid4()),
        direct_ownership=True
    )
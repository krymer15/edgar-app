# tests/forms/transaction/conftest.py
import pytest
from sqlalchemy import create_engine, Column, String, Text, TIMESTAMP, func, CheckConstraint, ForeignKey, Date, Numeric, Index, MetaData, Boolean, ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship
import uuid

# Create a separate Base class for test models
TestBase = declarative_base(metadata=MetaData())

# Create simplified test models
class TestEntity(TestBase):
    __tablename__ = "test_entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cik = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TestFiling(TestBase):
    __tablename__ = "test_form4_filings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TestRelationship(TestBase):
    __tablename__ = "test_form4_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("test_form4_filings.id"), nullable=False)
    issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("test_entities.id"), nullable=False)
    owner_entity_id = Column(UUID(as_uuid=True), ForeignKey("test_entities.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TestSecurity(TestBase):
    __tablename__ = "test_securities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("test_entities.id"), nullable=False)
    security_type = Column(String, nullable=False)
    standard_cusip = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TestDerivativeSecurity(TestBase):
    __tablename__ = "test_derivative_securities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    security_id = Column(UUID(as_uuid=True), ForeignKey("test_securities.id"), nullable=False)
    underlying_security_id = Column(UUID(as_uuid=True), ForeignKey("test_securities.id"))
    underlying_security_title = Column(String, nullable=False)
    conversion_price = Column(Numeric)
    exercise_date = Column(Date)
    expiration_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TestNonDerivativeTransaction(TestBase):
    __tablename__ = "test_non_derivative_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("test_form4_filings.id"), nullable=False)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("test_form4_relationships.id"), nullable=False)
    security_id = Column(UUID(as_uuid=True), ForeignKey("test_securities.id"), nullable=False)
    transaction_code = Column(String, nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_form_type = Column(String)
    shares_amount = Column(Numeric, nullable=False)
    price_per_share = Column(Numeric)
    direct_ownership = Column(Boolean, nullable=False, default=True)
    ownership_nature_explanation = Column(String)
    transaction_timeliness = Column(String)
    footnote_ids = Column(ARRAY(String))
    acquisition_disposition_flag = Column(String, nullable=False)
    is_part_of_group_filing = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TestDerivativeTransaction(TestBase):
    __tablename__ = "test_derivative_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form4_filing_id = Column(UUID(as_uuid=True), ForeignKey("test_form4_filings.id"), nullable=False)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("test_form4_relationships.id"), nullable=False)
    security_id = Column(UUID(as_uuid=True), ForeignKey("test_securities.id"), nullable=False)
    derivative_security_id = Column(UUID(as_uuid=True), ForeignKey("test_derivative_securities.id"), nullable=False)
    transaction_code = Column(String, nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_form_type = Column(String)
    derivative_shares_amount = Column(Numeric, nullable=False)
    price_per_derivative = Column(Numeric)
    underlying_shares_amount = Column(Numeric)
    direct_ownership = Column(Boolean, nullable=False, default=True)
    ownership_nature_explanation = Column(String)
    transaction_timeliness = Column(String)
    footnote_ids = Column(ARRAY(String))
    acquisition_disposition_flag = Column(String, nullable=False)
    is_part_of_group_filing = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

# Use an in-memory SQLite database for tests
@pytest.fixture(scope="function")
def engine():
    engine = create_engine("sqlite:///:memory:")
    TestBase.metadata.create_all(engine)
    yield engine
    TestBase.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Creates a new database session for testing"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def test_entity(db_session):
    """Create a test entity for transaction tests"""
    entity = TestEntity(
        id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
        cik="0001234567",
        name="Test Company",
        entity_type="company"
    )
    db_session.add(entity)
    db_session.commit()
    return entity

@pytest.fixture
def test_owner_entity(db_session):
    """Create a test owner entity for transaction tests"""
    entity = TestEntity(
        id=uuid.UUID('87654321-8765-4321-8765-432187654321'),
        cik="0007654321",
        name="Test Owner",
        entity_type="person"
    )
    db_session.add(entity)
    db_session.commit()
    return entity

@pytest.fixture
def test_filing(db_session):
    """Create a test filing for transaction tests"""
    filing = TestFiling(
        id=uuid.UUID('11111111-1111-1111-1111-111111111111'),
        document_id="test-document-123"
    )
    db_session.add(filing)
    db_session.commit()
    return filing

@pytest.fixture
def test_relationship(db_session, test_entity, test_owner_entity, test_filing):
    """Create a test relationship for transaction tests"""
    relationship = TestRelationship(
        id=uuid.UUID('22222222-2222-2222-2222-222222222222'),
        form4_filing_id=test_filing.id,
        issuer_entity_id=test_entity.id,
        owner_entity_id=test_owner_entity.id
    )
    db_session.add(relationship)
    db_session.commit()
    return relationship

@pytest.fixture
def test_security(db_session, test_entity):
    """Create a test security for transaction tests"""
    security = TestSecurity(
        id=uuid.UUID('33333333-3333-3333-3333-333333333333'),
        title="Common Stock",
        issuer_entity_id=test_entity.id,
        security_type="equity"
    )
    db_session.add(security)
    db_session.commit()
    return security

@pytest.fixture
def test_derivative_security(db_session, test_security):
    """Create a test derivative security for transaction tests"""
    derivative = TestDerivativeSecurity(
        id=uuid.UUID('44444444-4444-4444-4444-444444444444'),
        security_id=test_security.id,
        underlying_security_title="Common Stock Option",
        conversion_price=Decimal("10.00")
    )
    db_session.add(derivative)
    db_session.commit()
    return derivative
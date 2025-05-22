# tests/forms/security/conftest.py
import pytest
from sqlalchemy import create_engine, Column, String, Text, TIMESTAMP, func, CheckConstraint, ForeignKey, Date, Numeric, Index, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship
import uuid

# Create a separate Base class for test models
TestBase = declarative_base(metadata=MetaData())

# Create simplified test models for both entities and securities
class TestEntity(TestBase):
    __tablename__ = "test_entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cik = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
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

    # Relationships
    issuer_entity = relationship("TestEntity", foreign_keys=[issuer_entity_id])
    derivative_security = relationship("TestDerivativeSecurity", back_populates="security", uselist=False)

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

    # Relationships
    security = relationship("TestSecurity", foreign_keys=[security_id], back_populates="derivative_security")
    underlying_security = relationship("TestSecurity", foreign_keys=[underlying_security_id])

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
    """Create a test entity for security tests"""
    entity = TestEntity(
        id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
        cik="0001234567",
        name="Test Company",
        entity_type="company"
    )
    db_session.add(entity)
    db_session.commit()
    return entity
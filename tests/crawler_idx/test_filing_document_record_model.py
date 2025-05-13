
import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from sqlalchemy import inspect, create_engine
from models.orm_models.filing_metadata import FilingMetadata
from models.orm_models.filing_document_orm import FilingDocumentORM
from models.dataclasses.filing_document_record import FilingDocumentRecord as FilingDocDC
from models.adapters.dataclass_to_orm import convert_filing_doc_to_orm
from models.base import Base
from sqlalchemy.orm import Session
import uuid

def test_orm_mapping_matches_ddl():
    mapper = inspect(FilingDocumentORM)
    cols = {c.key: c for c in mapper.columns}

    # Primary key
    assert cols["id"].primary_key

    # Foreign key to filing_metadata.accession_number
    fks = cols["accession_number"].foreign_keys
    assert any("filing_metadata.accession_number" in str(fk.column) for fk in fks)

    # Required fields exist
    for field in [
        "cik", "document_type", "filename", "description",
        "source_url", "source_type", "is_primary",
        "is_exhibit", "is_data_support", "accessible"
    ]:
        assert field in cols

    # Defaults / server defaults
    assert "CURRENT_TIMESTAMP" in str(cols["created_at"].server_default.arg)
    assert "CURRENT_TIMESTAMP" in str(cols["updated_at"].server_default.arg)

@pytest.fixture
def temp_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_filing_document_roundtrip(temp_db):
    dc = FilingDocDC(
        accession_number="0001234567-25-000001",
        cik="0001234567",
        document_type="sgml",
        filename="example.txt",
        description="Test doc",
        source_url="https://example.com/doc.txt",
        source_type="sgml",
        is_primary=True,
        is_exhibit=False,
        is_data_support=False,
        accessible=True,
    )

    orm = convert_filing_doc_to_orm(dc)
    orm.id = uuid.uuid4()
    temp_db.add(orm)
    temp_db.commit()

    fetched = temp_db.query(type(orm)).filter_by(accession_number=dc.accession_number).first()
    assert fetched.filename == dc.filename
    assert fetched.cik == dc.cik
    assert fetched.is_primary is True
    assert fetched.accessible is True
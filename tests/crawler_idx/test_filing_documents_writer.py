# tests/crawler_idx/test_filing_documents_writer.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from models.base import Base
from models.orm_models.filing_documents import FilingDocument as FilingDocORM
from models.dataclasses.filing_document import FilingDocument as FilingDocDC
from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter


@pytest.fixture(scope="function")
def test_db_session():
    # In-memory SQLite for isolated testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    clear_mappers()


def test_write_documents_insert_update_skip(test_db_session):
    writer = FilingDocumentsWriter(db_session=test_db_session)

    # First batch: two unique entries
    doc1 = FilingDocDC(
        accession_number="0000001",
        cik="1234567890",
        document_type="EX-99.1",
        filename="doc1.txt",
        description="First doc",
        source_url="https://sec.gov/doc1.txt",
        source_type="html",
        is_primary=True
    )
    doc2 = FilingDocDC(
        accession_number="0000002",
        cik="1234567890",
        document_type="EX-99.2",
        filename="doc2.txt",
        description="Second doc",
        source_url="https://sec.gov/doc2.txt",
        source_type="html",
        is_exhibit=True
    )

    writer.write_documents([doc1, doc2])

    # Check: 2 inserted
    results = test_db_session.query(FilingDocORM).all()
    assert len(results) == 2
    assert results[0].description == "First doc"

    # Second batch: update doc1, skip doc2 (unchanged)
    doc1_updated = FilingDocDC(
        accession_number="0000001",
        cik="1234567890",
        document_type="EX-99.1",
        filename="doc1.txt",
        description="Updated description",
        source_url="https://sec.gov/doc1.txt",
        source_type="html",
        is_primary=True
    )
    doc2_unchanged = doc2

    writer.write_documents([doc1_updated, doc2_unchanged])

    # Check: still 2 records, doc1 updated
    results = test_db_session.query(FilingDocORM).all()
    assert len(results) == 2
    updated_doc1 = test_db_session.query(FilingDocORM).filter_by(accession_number="0000001").first()
    assert updated_doc1.description == "Updated description"

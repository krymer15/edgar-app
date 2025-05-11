
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
from sqlalchemy.orm import sessionmaker
from models.base import Base
from writers.crawler_idx.filing_metadata_writer import FilingMetadataWriter
from models.dataclasses.filing_metadata import FilingMetadata
from datetime import date

@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session
    Base.metadata.drop_all(engine)

def test_upsert_many_inserts_and_updates(test_db):
    session = test_db()
    writer = FilingMetadataWriter()
    writer.session = session

    record = FilingMetadata(
        accession_number="0000000000-01-000001",
        cik="0000000000",
        form_type="10-K",
        filing_date=date(2024, 1, 1),
        filing_url="https://example.com/10-K"
    )

    # First insert
    writer.upsert_many([record])

    # Update with new URL
    record.filing_url = "https://example.com/10-K-updated"
    writer.upsert_many([record])

    # Query via ORM model
    from models.orm_models.filing_metadata import FilingMetadata as FilingMetadataORM
    result = session.query(FilingMetadataORM).all()

    assert len(result) == 1
    assert result[0].filing_url == "https://example.com/10-K-updated"

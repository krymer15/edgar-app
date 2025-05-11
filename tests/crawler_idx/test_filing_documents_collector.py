# tests/crawler_idx/test_filing_documents_collector.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from collectors.crawler_idx.filing_documents_collector import FilingDocumentsCollector
from models.orm_models.filing_metadata import FilingMetadata as FilingMetadataORM
from models.base import Base
from unittest.mock import patch

from config.config_loader import ConfigLoader
from pathlib import Path

FIXTURE_SGML_PATH = Path("tests/fixtures/0000921895-25-001190.txt")


@pytest.fixture(scope="module")
def test_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture
def sample_metadata_record(test_db_session):
    record = FilingMetadataORM(
        accession_number="0000921895-25-001190",
        cik="0000921895",
        form_type="8-K",
        filing_date=datetime.date(2025, 5, 10),
        filing_url="https://www.sec.gov/Archives/edgar/data/921895/000092189525001190/0000921895-25-001190.txt"
    )
    test_db_session.add(record)
    test_db_session.commit()
    return record


def test_collect_returns_expected_documents(test_db_session, sample_metadata_record):
    fixture_text = FIXTURE_SGML_PATH.read_text(encoding="utf-8")

    with patch("downloaders.sgml_downloader.SgmlDownloader.download_sgml", return_value=fixture_text):
        config = ConfigLoader.load_config()
        user_agent = config["sec_downloader"]["user_agent"]

        collector = FilingDocumentsCollector(db_session=test_db_session, user_agent=user_agent)
        results = collector.collect("2025-05-10")

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(hasattr(doc, "accession_number") for doc in results)
        assert all(doc.accessible for doc in results)

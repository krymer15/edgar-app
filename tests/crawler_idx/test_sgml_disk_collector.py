# tests/crawler_idx/test_sgml_isk_collector.py

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
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.orm_models.filing_document_orm import FilingDocumentORM
from models.orm_models.filing_metadata import FilingMetadata
from models.dataclasses.sgml_text_document import SgmlTextDocument
from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector
from config.config_loader import ConfigLoader


@pytest.fixture(scope="function")
def test_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_sgml_record(test_db_session):
    # Insert filing_metadata
    meta = FilingMetadata(
        accession_number="0000000000-25-000001",
        cik="0000000000",
        form_type="10-K",
        filing_date=datetime.date(2025, 5, 10),
        filing_url="https://example.com"
    )
    test_db_session.add(meta)

    # Insert filing_document
    doc = FilingDocumentORM(
        accession_number=meta.accession_number,
        cik=meta.cik,
        document_type="10-K",
        filename="submission.txt",
        source_url="https://example.com/0000000000-25-000001.txt",
        source_type="sgml",
        is_primary=True,
    )
    test_db_session.add(doc)
    test_db_session.commit()
    return doc


def test_sgml_disk_collector_writes_file(tmp_path, monkeypatch, test_db_session, sample_sgml_record):
    config = ConfigLoader.load_config()
    user_agent = config["sec_downloader"]["user_agent"]

    # Patch base_data_path to tmp
    monkeypatch.setitem(
        __import__("utils.path_manager").path_manager.STORAGE_CONFIG,
        "base_data_path",
        str(tmp_path)
    )

    # Patch download_sgml to return dummy content
    with patch("downloaders.sgml_downloader.SgmlDownloader.download_sgml") as mock_dl:
        mock_dl.return_value = SgmlTextDocument(
            cik=sample_sgml_record.cik,
            accession_number=sample_sgml_record.accession_number,
            content="Mock SGML content"
        )

        collector = SgmlDiskCollector(
            db_session=test_db_session,
            user_agent=user_agent,
            use_cache=True,
            write_cache=True
        )
        results = collector.collect("2025-05-10")

        # Validate file write
        assert len(results) == 1
        written_path = results[0]
        assert os.path.exists(written_path)
        with open(written_path, "r", encoding="utf-8") as f:
            assert "Mock SGML content" in f.read()

        # Run again — should skip write
        results2 = collector.collect("2025-05-10")
        assert results2 == []
# tests/orchestrators/crawler_idx/test_filing_metadata_orchestrator.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator
from models.dataclasses.filing_metadata import FilingMetadata

@pytest.fixture
def mock_metadata():
    return [
        FilingMetadata(
            cik="0000123456",
            form_type="10-K",
            filing_date=date(2024, 12, 31),
            filing_url="https://www.sec.gov/Archives/edgar/data/0000123456/0000123456-24-000001-index.htm",
            accession_number="0000123456-24-000001"
        )
    ]

@patch("orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataCollector")
@patch("orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataWriter")
def test_orchestrator_calls_collector_and_writer(mock_writer_cls, mock_collector_cls, mock_metadata):
    # Mock collector and writer
    mock_collector = mock_collector_cls.return_value
    mock_writer = mock_writer_cls.return_value

    # Return mock data from collector
    mock_collector.collect.return_value = mock_metadata
    mock_writer.upsert_many = MagicMock()

    # Run orchestrator
    orchestrator = FilingMetadataOrchestrator()
    orchestrator.run("2024-12-31")

    # Assertions
    mock_collector.collect.assert_called_once_with("2024-12-31")
    mock_writer.upsert_many.assert_called_once_with(mock_metadata)

def test_orchestrator_respects_limit(mock_metadata):
    with patch("orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataCollector") as mock_collector_cls, \
         patch("orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataWriter") as mock_writer_cls:

        # Expand mock metadata to simulate a large input
        mock_records = mock_metadata * 5  # 5 copies = 5 records
        mock_collector = mock_collector_cls.return_value
        mock_writer = mock_writer_cls.return_value

        mock_collector.collect.return_value = mock_records
        mock_writer.upsert_many = MagicMock()

        orchestrator = FilingMetadataOrchestrator()
        orchestrator.run("2024-12-31", limit=2)

        mock_collector.collect.assert_called_once_with("2024-12-31")

        # Ensure only 2 records were passed to writer
        args, _ = mock_writer.upsert_many.call_args
        assert len(args[0]) == 2

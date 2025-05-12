# tests/crawler_idx/test_filing_documents_orchestrator.py

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
from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from models.dataclasses.filing_document_record import FilingDocumentRecord

@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.ConfigLoader")
def test_run_calls_orchestrate_and_writer(mock_config_loader, mock_get_db_session, mock_writer_cls, mock_collector_cls):
    # Setup mocks
    mock_config_loader.load_config.return_value = {
        "sec_downloader": {"user_agent": "TestBot/1.0"}
    }
    mock_get_db_session.return_value = MagicMock()

    mock_collector_instance = MagicMock()
    mock_writer_instance = MagicMock()
    mock_doc = FilingDocumentRecord(
        accession_number="0001234567-21-000001",
        cik="1234567",
        document_type="primary",
        filename="0001234567-21-000001.txt",
        description="Test Document",
        source_url="https://example.com/test.txt",
        source_type="sgml",
        is_primary=True,
        is_exhibit=False,
        accessible=True,
    )

    mock_collector_instance.collect.return_value = [mock_doc]
    mock_collector_cls.return_value = mock_collector_instance
    mock_writer_cls.return_value = mock_writer_instance

    orchestrator = FilingDocumentsOrchestrator()
    orchestrator.run(target_date="2025-05-01", limit=None)

    # Assertions
    mock_collector_instance.collect.assert_called_once_with("2025-05-01")
    mock_writer_instance.write_documents.assert_called_once_with([mock_doc])

@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.ConfigLoader")
def test_run_respects_limit(mock_config_loader, mock_get_db_session, mock_writer_cls, mock_collector_cls):
    mock_config_loader.load_config.return_value = {
        "sec_downloader": {"user_agent": "TestBot/1.0"}
    }
    mock_get_db_session.return_value = MagicMock()

    mock_collector_instance = MagicMock()
    mock_writer_instance = MagicMock()
    mock_docs = [MagicMock() for _ in range(5)]

    mock_collector_instance.collect.return_value = mock_docs
    mock_collector_cls.return_value = mock_collector_instance
    mock_writer_cls.return_value = mock_writer_instance

    orchestrator = FilingDocumentsOrchestrator()
    orchestrator.run(target_date="2025-05-01", limit=3)

    mock_collector_instance.collect.assert_called_once_with("2025-05-01")
    mock_writer_instance.write_documents.assert_called_once_with(mock_docs[:3])

@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.ConfigLoader")
def test_run_raises_and_logs_on_error(mock_config_loader, mock_get_db_session, mock_writer_cls, mock_collector_cls):
    mock_config_loader.load_config.return_value = {
        "sec_downloader": {"user_agent": "TestBot/1.0"}
    }
    mock_get_db_session.return_value = MagicMock()

    mock_collector_instance = MagicMock()
    mock_collector_instance.collect.side_effect = RuntimeError("Boom")
    mock_collector_cls.return_value = mock_collector_instance
    mock_writer_cls.return_value = MagicMock()

    orchestrator = FilingDocumentsOrchestrator()

    with pytest.raises(RuntimeError, match="Boom"):
        orchestrator.run(target_date="2025-05-01")

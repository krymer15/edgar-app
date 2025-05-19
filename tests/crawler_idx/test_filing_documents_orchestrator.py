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
    mock_collector_instance.collect.assert_called_once_with("2025-05-01", limit=None)
    mock_writer_instance.write_documents.assert_called_once_with([mock_doc])

@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.ConfigLoader")
def test_run_respects_limit_for_date_based_queries(mock_config_loader, mock_get_db_session, mock_writer_cls, mock_collector_cls):
    """Test that limit is applied for date-based queries."""
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

    # The collector should receive the limit parameter
    mock_collector_instance.collect.assert_called_once()
    args, kwargs = mock_collector_instance.collect.call_args
    assert kwargs["target_date"] == "2025-05-01"
    assert kwargs["limit"] == 3  # Limit is passed through
    assert "accession_filters" not in kwargs or kwargs["accession_filters"] is None
    
    # Writer should receive all documents returned by the collector
    mock_writer_instance.write_documents.assert_called_once_with(mock_docs)

@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.ConfigLoader")
def test_limit_ignored_for_specific_accessions(mock_config_loader, mock_get_db_session, mock_writer_cls, mock_collector_cls):
    """Test that limit is ignored when processing specific accessions."""
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

    # Create accession list
    accessions = ["0001234567-25-000001", "0001234567-25-000002"]
    
    orchestrator = FilingDocumentsOrchestrator()
    orchestrator.run(accession_filters=accessions, limit=3)  # Limit should be ignored

    # The collector should receive None for limit when accession_filters is provided
    mock_collector_instance.collect.assert_called_once()
    args, kwargs = mock_collector_instance.collect.call_args
    assert kwargs["target_date"] is None
    assert kwargs["limit"] is None  # Limit should be None when accession_filters is provided
    assert kwargs["accession_filters"] == accessions
    
    # Writer should receive all documents returned by the collector
    mock_writer_instance.write_documents.assert_called_once_with(mock_docs)

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

@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.filing_documents_orchestrator.ConfigLoader")
def test_init_passes_write_cache_and_downloader(mock_config_loader, mock_get_db_session, mock_collector_cls, mock_writer_cls):
    mock_config_loader.load_config.return_value = {
        "sec_downloader": {"user_agent": "TestBot/1.0"}
    }

    from downloaders.sgml_downloader import SgmlDownloader
    downloader = SgmlDownloader(user_agent="TestAgent", use_cache=True)

    orchestrator = FilingDocumentsOrchestrator(
        use_cache=True,
        write_cache=False,
        downloader=downloader
    )

    # Check that FilingDocumentsCollector was initialized with expected args
    args, kwargs = mock_collector_cls.call_args

    assert kwargs["use_cache"] is True
    assert kwargs["write_cache"] is False
    assert kwargs["downloader"] is not None
    from downloaders.sgml_downloader import SgmlDownloader
    assert isinstance(kwargs["downloader"], SgmlDownloader)

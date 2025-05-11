# tests/test_daily_ingestion_orchestrator.py

from unittest.mock import patch, MagicMock
from orchestrators.crawler_idx.daily_ingestion_orchestrator import DailyIngestionOrchestrator

@patch("orchestrators.daily_ingestion_orchestrator.FilingMetadataOrchestrator")
@patch("orchestrators.daily_ingestion_orchestrator.FilingDocumentsOrchestrator")
def test_daily_ingestion_calls_both_orchestrators(mock_docs_cls, mock_meta_cls):
    # Mock run() methods
    mock_meta_instance = MagicMock()
    mock_docs_instance = MagicMock()
    mock_meta_cls.return_value = mock_meta_instance
    mock_docs_cls.return_value = mock_docs_instance

    orchestrator = DailyIngestionOrchestrator(user_agent="TestAgent/1.0")
    orchestrator.run(date_str="2025-04-28")

    # Assert orchestrators were initialized and run was called
    mock_meta_cls.assert_called_once_with("TestAgent/1.0")
    mock_docs_cls.assert_called_once_with()
    mock_meta_instance.run.assert_called_once_with("2025-04-28")
    mock_docs_instance.run.assert_called_once_with("2025-04-28")

@patch("orchestrators.daily_ingestion_orchestrator.FilingMetadataOrchestrator")
@patch("orchestrators.daily_ingestion_orchestrator.FilingDocumentsOrchestrator")
def test_skip_flags_respected(mock_docs_cls, mock_meta_cls):
    mock_meta = MagicMock()
    mock_docs = MagicMock()
    mock_meta_cls.return_value = mock_meta
    mock_docs_cls.return_value = mock_docs

    orchestrator = DailyIngestionOrchestrator(user_agent="TestAgent/1.0")
    orchestrator.run(date_str="2025-04-28", skip_meta=True, skip_docs=False)

    mock_meta.run.assert_not_called()
    mock_docs.run.assert_called_once_with("2025-04-28")

    orchestrator.run(date_str="2025-04-28", skip_meta=False, skip_docs=True)
    mock_meta.run.assert_called_once_with("2025-04-28")  # called once cumulatively
    mock_docs.run.assert_called_once()  # no second call

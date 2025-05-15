# tests/crawler_idx/test_sgml_disk_orchestrator.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from unittest.mock import patch, MagicMock
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator

@patch("orchestrators.crawler_idx.sgml_disk_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.sgml_disk_orchestrator.SgmlDiskCollector")
def test_sgml_disk_orchestrator_runs(mock_collector_cls, mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    mock_collector = MagicMock()
    mock_collector.collect.return_value = ["fake_path_1.txt", "fake_path_2.txt"]
    mock_collector_cls.return_value = mock_collector

    orchestrator = SgmlDiskOrchestrator(use_cache=True, write_cache=True)
    results = orchestrator.orchestrate("2025-05-10")

    assert isinstance(results, list)
    assert len(results) == 2
    assert "fake_path_1.txt" in results
    assert mock_collector.collect.called

@patch("orchestrators.crawler_idx.sgml_disk_orchestrator.get_db_session")
@patch("orchestrators.crawler_idx.sgml_disk_orchestrator.SgmlDiskCollector")
def test_orchestrator_passes_configured_args(mock_collector_cls, mock_get_db_session):
    from downloaders.sgml_downloader import SgmlDownloader

    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    mock_collector = MagicMock()
    mock_collector.collect.return_value = []
    mock_collector_cls.return_value = mock_collector

    downloader = SgmlDownloader(user_agent="TestBot", use_cache=False)

    orchestrator = SgmlDiskOrchestrator(
        use_cache=False,
        write_cache=False,
        downloader=downloader
    )
    orchestrator.orchestrate(target_date="2025-05-10", accession_filters=None, limit=1)

    # Validate call args to collector
    _, kwargs = mock_collector_cls.call_args
    assert kwargs["use_cache"] is False
    assert kwargs["write_cache"] is False
    assert kwargs["downloader"] is downloader
    assert kwargs.get("accession_filters") is None

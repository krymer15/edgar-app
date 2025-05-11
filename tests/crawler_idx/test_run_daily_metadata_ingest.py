# tests/test_run_daily_metadata_ingest.py

import os, sys

# === [Universal Header] Add project root to path ===
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from unittest import mock
from scripts.crawler_idx import run_daily_metadata_ingest


@pytest.fixture
def mock_orchestrator_run():
    with mock.patch(
        "scripts.crawler_idx.run_daily_metadata_ingest.FilingMetadataOrchestrator"
    ) as mock_orchestrator_cls:
        mock_instance = mock_orchestrator_cls.return_value
        yield mock_instance.run


def test_cli_runs_with_date(monkeypatch, mock_orchestrator_run):
    test_args = [
        "run_daily_metadata_ingest.py",
        "--date",
        "2024-12-20",
        "--limit",
        "10",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    run_daily_metadata_ingest.main()

    mock_orchestrator_run.assert_called_once_with(date_str="2024-12-20", limit=10)


def test_cli_runs_with_backfill(monkeypatch, mock_orchestrator_run):
    test_args = [
        "run_daily_metadata_ingest.py",
        "--backfill",
        "2",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    run_daily_metadata_ingest.main()
    assert mock_orchestrator_run.call_count == 2

def test_cli_errors_without_date_or_backfill(monkeypatch):
    test_args = [
        "run_daily_metadata_ingest.py"
        ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        run_daily_metadata_ingest.main()
    assert exc_info.value.code == 1


def test_cli_fails_with_invalid_date_format(monkeypatch):
    test_args = [
        "run_daily_metadata_ingest.py",
        "--date",
        "12-20-2024"  # Wrong format
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        run_daily_metadata_ingest.main()
    # argparse exits with code 2 on argument parse error
    assert exc_info.value.code == 2

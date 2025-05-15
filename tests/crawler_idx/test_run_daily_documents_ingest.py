# tests/crawler_idx/test_run_daily_documents_ingest.py

import subprocess
from datetime import datetime, timedelta, timezone

def test_run_daily_documents_ingest():
    test_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    result = subprocess.run(
        [
            "python",
            "scripts/crawler_idx/run_daily_documents_ingest.py",
            "--date", test_date,
            "--limit", "5"
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Starting filing document ingestion" in result.stdout

def test_run_daily_documents_ingest_basic():
    test_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    result = subprocess.run(
        [
            "python",
            "scripts/crawler_idx/run_daily_documents_ingest.py",
            "--date", test_date,
            "--limit", "2"
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Starting filing document ingestion" in result.stdout


# tests/crawler_idx/test_run_daily_documents_ingest.py

import subprocess
from datetime import datetime, timedelta

def test_run_daily_documents_ingest():
    test_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
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

# tests/crawler_idx/test_run_daily_pipeline_ingest.py

import subprocess
import types
import sys, os

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

from pathlib import Path
from dotenv import load_dotenv

SCRIPT = Path("scripts/crawler_idx/run_daily_pipeline_ingest.py")
load_dotenv()

from downloaders.sgml_downloader import SgmlDownloader
from models.dataclasses.sgml_text_document import SgmlTextDocument
from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionPipeline
    
def mock_download_sgml(self, cik: str, accession_number: str, write_cache: bool = True) -> SgmlTextDocument:
    with open("tests/fixtures/0000925421-24-000007.txt", "r", encoding="utf-8") as f:
        return SgmlTextDocument(
            cik=cik,
            accession_number=accession_number,
            content=f.read()
        )

SgmlDownloader.download_sgml = types.MethodType(mock_download_sgml, SgmlDownloader)

APP_CONFIG_PATH = "tests/fixtures/app_config_test.yaml"
TARGET_DATE = "2024-05-01"

def test_pipeline_direct_call():
    """Bypass subprocess: test pipeline directly in-process with monkeypatches"""
    from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionPipeline

    pipeline = DailyIngestionPipeline(use_cache=False)
    pipeline.run(target_date="2024-05-01", limit=1)

def test_pipeline_log_output_includes_all_stages():
    """Sanity test: confirms orchestrator logs contain all major stage markers"""
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"

    env = os.environ.copy()
    env["APP_CONFIG"] = APP_CONFIG_PATH
    env["TEST_SINGLE_ACCESSION"] = "true"

    result = subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", TARGET_DATE,
        "--limit", "1",
        # "--no_cache"
    ], capture_output=True, text=True, env=env)

    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    assert "[INFO] [META] Starting filing metadata ingestion" in result.stdout
    assert "[INFO] [DOCS] Starting document indexing" in result.stdout
    assert "[INFO] [SGML] Starting SGML disk download" in result.stdout

def test_pipeline_writes_expected_sgml_file():
    """Integration test: runs CLI and confirms expected SGML .txt file is written to disk"""
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"

    env = os.environ.copy()
    env["APP_CONFIG"] = APP_CONFIG_PATH
    env["TEST_SINGLE_ACCESSION"] = "true"

    result = subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", TARGET_DATE,
        "--limit", "1",
        # "--no_cache"
    ], capture_output=True, text=True, env=env)

    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"

    # Confirm expected SGML .txt file was written to final raw path
    expected_accession = "0000925421-24-000007"
    expected_cik = "1930609"
    expected_year = "2024"

    expected_path = Path(
        f"test_data/raw/{expected_cik}/{expected_year}/D_A/{expected_accession}/{expected_accession}.txt"
    )

    assert expected_path.exists(), f"Expected SGML file not found: {expected_path}"

    # Optional: view first 300 characters
    print(f"\n Output file preview:\n{expected_path}\n")
    with open(expected_path, "r", encoding="utf-8") as f:
        print(f.read(300))

def test_pipeline_skips_holiday_or_weekend():
    """Test that the CLI exits gracefully on SEC holidays or weekends"""
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"

    env = os.environ.copy()
    env["APP_CONFIG"] = APP_CONFIG_PATH

    result = subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", "2025-05-10",  # Saturday
        "--limit", "1"
    ], capture_output=True, text=True, env=env)

    print(result.stdout)
    print(result.stderr)

    assert result.returncode == 0, "Expected graceful exit on invalid filing day"
    assert "not a valid SEC filing day" in result.stdout

def test_pipeline_avoids_redundant_sgml_download(monkeypatch):
    call_counter = {"count": 0}

    def mocked_download_html(self, url):
        call_counter["count"] += 1
        return "test SGML content"

    monkeypatch.setattr(SgmlDownloader, "download_html", mocked_download_html)

    pipeline = DailyIngestionPipeline(use_cache=True)
    pipeline.run(target_date="2025-05-12", limit=1)

    assert call_counter["count"] == 1, "SGML downloaded more than once!"
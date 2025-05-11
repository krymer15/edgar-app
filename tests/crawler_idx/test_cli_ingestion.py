# tests/test_cli_ingestion.py

import subprocess
import sys, os
from pathlib import Path
from dotenv import load_dotenv

SCRIPT = Path("scripts/run_daily_ingestion.py")
load_dotenv()  # 👈 ensure env vars from .env are loaded into this test process

def test_cli_runs_and_prints_metadata_only():
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"

    env = os.environ.copy()  # 👈 inherit and pass all env vars to subprocess
    env["APP_CONFIG"] = "tests/tmp/app_config_test.yaml" # Set APP_CONFIG in CLI test code

    result = subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", "2025-04-28",
        "--limit", "1",
        "--skip_docs"
    ], capture_output=True, text=True, env=env)

    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    assert "[META] Running metadata ingestion" in result.stdout or "[META] Running metadata ingestion" in result.stdout

def test_cli_runs_and_prints_docs_only():
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"

    env = os.environ.copy()  # 👈 inherit and pass all env vars to subprocess
    env["APP_CONFIG"] = "tests/tmp/app_config_test.yaml" # Set APP_CONFIG in CLI test code

    result = subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", "2025-04-28",
        "--limit", "1",
        "--skip_meta"
    ], capture_output=True, text=True, env=env)

    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    assert "Running FilingDocumentsOrchestrator" in result.stdout or "Running FilingDocumentsOrchestrator" in result.stdout

def test_cli_runs_both_steps():

    env = os.environ.copy()  # 👈 inherit and pass all env vars to subprocess
    env["APP_CONFIG"] = "tests/tmp/app_config_test.yaml" # Set APP_CONFIG in CLI test code

    result = subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", "2025-04-28",
        "--limit", "1"
    ], capture_output=True, text=True, env=env)

    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    assert "[META] Running metadata ingestion" in result.stdout or "[META] Running metadata ingestion" in result.stdout
    assert "Running FilingDocumentsOrchestrator" in result.stdout or "Running FilingDocumentsOrchestrator" in result.stdout

def test_cli_writes_raw_file_to_disk():
    """
    ✅ This integration test verifies that running the CLI with --skip_meta writes a raw .txt file
    to the location defined by base_data_path in the test app_config.
    
    It assumes the FilingDocumentsOrchestrator downloads and stores SGML .txt content 
    using path_manager.build_raw_filepath().
    
    This test DOES write to disk and should be paired with a cleanup routine for `test_data/`.
    """

    # Setup environment with test config override
    env = os.environ.copy()
    env["APP_CONFIG"] = "tests/tmp/app_config_test.yaml"

    # Run CLI ingestion for a known accession number (limit = 1)
    subprocess.run([
        sys.executable, str(SCRIPT),
        "--date", "2025-04-28",
        "--limit", "1",
        "--skip_meta"
    ], capture_output=True, text=True, env=env)

    # Expected path logic based on 2025-04-28 and the sample file
    # Example path: tests/tmp/data/raw/2025/0001084869/4/0000921895-25-001190/form413866005_04282025.xml
    expected_folder = Path("tests/tmp/data/raw/2025/0001084869/4/0000921895-25-001190")
    files_found = list(expected_folder.glob("*.xml"))  # Use glob to avoid exact filename coupling

    assert expected_folder.exists(), f"Expected folder does not exist: {expected_folder}"
    assert files_found, f"No raw files found in: {expected_folder}"

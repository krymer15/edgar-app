# utils/report_logger.py

import csv
import sys
from pathlib import Path
from datetime import datetime, timezone
from utils.get_project_root import get_project_root
from utils.config_loader import ConfigLoader

# Load config
_config = ConfigLoader.load_config()
_log_level = _config.get("app", {}).get("log_level", "INFO").upper()

# Shared schema across all ingestion log rows
CSV_FIELDNAMES = [
    "timestamp",
    "run_id",
    "record_type",          # 'parsed', 'exhibit', or 'summary'
    "accession_number",
    "cik",
    "form_type",
    "filing_date",
    "exhibits_written",
    "exhibits_skipped",
    "primary_doc_url"
]

def append_ingestion_report(row: dict, run_id: str = "", output_path: str = None):
    """Appends a structured row to the daily ingestion_report_YYYY-MM-DD.csv file."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Ensure required values are present
    row_with_defaults = {
        "timestamp": timestamp,
        "run_id": run_id,
        "record_type": row.get("record_type", "parsed"),
        "accession_number": row.get("accession_number", ""),
        "cik": row.get("cik", ""),
        "form_type": row.get("form_type", ""),
        "filing_date": row.get("filing_date", ""),
        "exhibits_written": row.get("exhibits_written", ""),
        "exhibits_skipped": row.get("exhibits_skipped", ""),
        "primary_doc_url": row.get("primary_doc_url", ""),
    }

    if output_path is None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        output_path = Path(get_project_root()) / "logs" / f"ingestion_report_{today}.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = output_path.is_file()

    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_with_defaults)

def append_batch_summary(total, skipped, failed, succeeded, run_id: str = "", output_path: str = None):
    """Appends a BATCH_SUMMARY row for the current run_id."""
    append_ingestion_report({
        "record_type": "summary",
        "accession_number": "BATCH_SUMMARY",
        "cik": "",
        "form_type": "",
        "filing_date": "",
        "exhibits_written": succeeded,
        "exhibits_skipped": skipped,
        "primary_doc_url": f"attempted={total}, failed={failed}"
    }, run_id=run_id, output_path=output_path)

# === Logging functions ===

def log_debug(message: str):
    if _log_level == "DEBUG":
        print(f"🐛 {message}", file=sys.stdout)

def log_info(message: str):
    if _log_level in ("DEBUG", "INFO"):
        print(f"ℹ️  {message}", file=sys.stdout)

def log_warn(message: str):
    if _log_level in ("DEBUG", "INFO", "WARNING"):
        print(f"⚠️  {message}", file=sys.stderr)

def log_error(message: str):
    print(f"❌ {message}", file=sys.stderr)

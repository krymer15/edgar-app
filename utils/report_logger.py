# utils/report_logger.py

import csv
import sys
from pathlib import Path
from datetime import datetime, timezone
from utils.get_project_root import get_project_root

# Avoid immediate import of ConfigLoader
_config = None
_log_level = None

def _load_config():
    """Load config lazily to avoid circular imports"""
    global _config, _log_level
    if _config is None:
        from config.config_loader import ConfigLoader
        _config = ConfigLoader.load_config()
        _log_level = _config.get("app", {}).get("log_level", "INFO").upper()

# Shared schema across all ingestion log rows
CSV_FIELDNAMES = [
    "timestamp",
    "record_type",          # 'parsed', 'exhibit', or 'summary'
    "accession_number",
    "cik",
    "form_type",
    "filing_date",
    "exhibits_written",
    "exhibits_skipped",
    "primary_doc_url"
]

def format_log_date(raw: str) -> str:
    try:
        return datetime.strptime(raw, "%Y%m%d").strftime("%Y-%m-%d") if len(raw) == 8 else raw
    except Exception:
        return raw

def append_ingestion_report(row: dict, output_path: str = None, log_date: str = None):
    """Appends a structured row to the daily ingestion_report_YYYY-MM-DD.csv file."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Ensure required values are present
    # `record_type` distinguishes between 'parsed', 'exhibit', and 'summary' rows.
    # Currently only 'parsed' and 'summary' are active. Future expansion will include exhibit-level logging.

    row_with_defaults = {
        "timestamp": timestamp,
        "record_type": row.get("record_type", "parsed"),
        "accession_number": row.get("accession_number", ""),
        "cik": row.get("cik", ""),
        "form_type": row.get("form_type", ""),
        "filing_date": row.get("filing_date", ""),
        "exhibits_written": int(row.get("exhibits_written") or 0),
        "exhibits_skipped": int(row.get("exhibits_skipped") or 0),
        "primary_doc_url": row.get("primary_doc_url", ""),
    }

    if output_path is None:
        log_file_date = format_log_date(log_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        output_path = Path(get_project_root()) / "logs" / f"ingestion_report_{log_file_date}.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = output_path.is_file()

    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_with_defaults)

def append_batch_summary(total, skipped, failed, succeeded, output_path: str = None, log_date: str = ""):
    """Appends a BATCH_SUMMARY row."""
    append_ingestion_report({
        "record_type": "summary",
        "accession_number": "BATCH_SUMMARY",
        "cik": "",
        "form_type": "",
        "filing_date": "",
        "exhibits_written": succeeded,
        "exhibits_skipped": skipped,
        "primary_doc_url": f"attempted={total}, failed={failed}"
    }, output_path=output_path, log_date=log_date)

# === Logging functions ===

def safe_print(message: str, stream=sys.stdout):
    try:
        print(message, file=stream)
    except UnicodeEncodeError:
        ascii_fallback = message.encode("ascii", errors="ignore").decode()
        print(ascii_fallback, file=stream)

def log_debug(message: str):
    # Load config lazily
    if _config is None:
        _load_config()
    
    # Get runtime config for current log level
    from config.config_loader import ConfigLoader
    runtime_config = ConfigLoader.load_config()
    level = runtime_config.get("app", {}).get("log_level", "INFO").upper()
    
    if level == "DEBUG":
        safe_print(f"[DEBUG] {message}", stream=sys.stdout)


def log_info(message: str):
    # Load config lazily
    if _config is None:
        _load_config()
        
    if _log_level in ("DEBUG", "INFO"):
        safe_print(f"[INFO] {message}", stream=sys.stdout)

def log_warn(message: str):
    # Load config lazily
    if _config is None:
        _load_config()
        
    if _log_level in ("DEBUG", "INFO", "WARNING"):
        safe_print(f"[WARN] {message}", stream=sys.stderr)

def log_error(message: str):
    safe_print(f"[ERROR] {message}", stream=sys.stderr)
'''
This CLI runner will:

✅ Download and parse the crawler.idx file

✅ Filter filings (unless --skip_filter is passed)

✅ Write to daily_index_metadata

✅ Parse SGML and write to parsed_sgml_metadata
'''

import sys
import os

# Insert project root into sys.path
try:
    from utils.get_project_root import get_project_root
    sys.path.insert(0, str(get_project_root()))
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from utils.config_loader import ConfigLoader
from orchestrators.batch_sgml_ingestion_orchestrator import BatchSgmlIngestionOrchestrator
from utils.report_logger import log_info

# ✅ Ensure project root is in sys.path — supports running from /scripts or /tests
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)  # insert(0) gives it import priority

# ✅ Parse CLI args
parser = argparse.ArgumentParser(description="Run SGML batch ingestion.")

parser.add_argument("--cik", help="CIK of the company")
parser.add_argument("--accession", help="Accession number of the filing")
parser.add_argument("--form_type", help="Form type (e.g., 8-K, 10-K)")
parser.add_argument("--filing_date", help="Filing date in YYYY-MM-DD format")
parser.add_argument("--save_raw", action="store_true", help="Save raw .txt to disk")
parser.add_argument("--date", help="Date to process crawler.idx (YYYY-MM-DD)", required=True)
parser.add_argument("--limit", type=int, help="Optional: limit number of filings")
parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging level")
parser.add_argument("--skip_filter", action="store_true", help="Skip global CIK/form_type filtering")
args = parser.parse_args()

log_info("📌 Note: This script also writes filtered filings to daily_index_metadata")

# ✅ Override config log level at runtime
if args.debug:
    config = ConfigLoader.load_config()
    config["app"]["log_level"] = "DEBUG"

if __name__ == "__main__":
    if not args.date:
        raise ValueError("⚠️ Please provide --date YYYY-MM-DD to run the batch ingestion.")
    
    orchestrator = BatchSgmlIngestionOrchestrator(
        date_str=args.date,
        limit=args.limit,
        override_filter=False if args.skip_filter else None
    )

    orchestrator.orchestrate()

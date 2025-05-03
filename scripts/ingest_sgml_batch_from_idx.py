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
parser.add_argument("--date", help="Date to process crawler.idx (YYYY-MM-DD)")
parser.add_argument("--limit", type=int, help="Optional: limit number of filings")
parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging level")
args = parser.parse_args()

# ✅ Override config log level at runtime
if args.debug:
    config = ConfigLoader.load_config()
    config["app"]["log_level"] = "DEBUG"

if __name__ == "__main__":
    orchestrator = BatchSgmlIngestionOrchestrator(date_str="2025-04-28", limit=5)
    orchestrator.orchestrate()

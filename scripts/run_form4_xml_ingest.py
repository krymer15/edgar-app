# scripts/run_form4_xml_ingest.py

"""
Dev-only CLI tool to ingest a single Form 4 XML file.

Usage:
    python scripts/run_form4_xml_ingest.py \
        --cik 921895 \
        --accession 0000921895-25-001190 \
        --filename xslF345X05_primary.xml \
        --date 2025-04-28
"""

import os, sys
import argparse
from dotenv import load_dotenv

# Ensure root is in sys.path
try:
    from utils.get_project_root import get_project_root
    sys.path.insert(0, str(get_project_root()))
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load config and db
from utils.config_loader import ConfigLoader
from orchestrators.form4_xml_orchestrator import Form4XmlOrchestrator
from utils.database import get_db_session

# Load .env + app_config.yaml
load_dotenv()
ConfigLoader.load_config() # triggers var expansion, logging, etc

def main():
    parser = argparse.ArgumentParser(description="Ingest a Form 4 XML file.")
    parser.add_argument("--cik", required=True, help="CIK without leading zeros")
    parser.add_argument("--accession", required=True, help="Full accession number")
    parser.add_argument("--filename", required=True, help="XML filename to download (e.g. xslF345X05_primary.xml)")
    parser.add_argument("--date", required=True, help="Filing date (YYYY-MM-DD)")
    args = parser.parse_args()

    meta = {
        "cik": args.cik,
        "accession_number": args.accession,
        "filing_date": args.date,
        "form_type": "4"
    }

    def log(msg):
        print(f"[Form4Runner] {msg}")

    session = get_db_session()
    orchestrator = Form4XmlOrchestrator(db_session=session, logger=log)
    orchestrator.run(meta=meta, filename=args.filename)

if __name__ == "__main__":
    main()
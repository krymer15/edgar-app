# scripts/crawler_idx/run_daily_documents_ingest.py

"""
Run SGML filing document ingestion from crawler.idx-derived metadata.

Usage:
    python scripts/crawler_idx/run_daily_documents_ingest.py --date 2024-12-20 --limit 50
    python scripts/crawler_idx/run_daily_documents_ingest.py --date 2024-12-20 --include_forms 10-K 8-K
"""

# 
# Pipeline 2: Filing Document Indexing (SGML)
#
# This CLI runner drives the second stage of the daily ingestion workflow.
# It performs the following:
# 1. Queries `filing_metadata` records from the database for a given date
# 2. Downloads the corresponding SGML `.txt` submissions (cached by default)
# 3. Uses `SgmlDocumentIndexer` to extract structured metadata for each internal document
# 4. Converts `FilingDocumentMetadata` → `FilingDocumentRecord`
# 5. Writes records to the `filing_documents` Postgres table
#
# Input: FilingMetadata records (from Pipeline 1)
# Output: FilingDocumentRecord rows (for downstream SGML and exhibit handling in Pipeline 3)


import os, sys
import argparse
from datetime import datetime

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from utils.report_logger import log_info, log_error
from utils.cache_manager import clear_sgml_cache
from config.config_loader import ConfigLoader

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD.")

def main():
    parser = argparse.ArgumentParser(description="Run SGML filing document ingestion.")
    parser.add_argument("--date", type=validate_date, required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Max number of documents to process")
    parser.add_argument("--include_forms", nargs="*", help="Only include specific form types (e.g. 10-K 8-K)")
    
    # Optional placeholder for --skip_forms, not yet implemented
    # parser.add_argument("--skip_forms", nargs="+", help="Form types to skip")

    args = parser.parse_args()

    orchestrator = FilingDocumentsOrchestrator(use_cache=False)
    try:
        log_info(f"[CLI] Starting filing document ingestion for {args.date} (limit={args.limit})")
        orchestrator.run(target_date=args.date, limit=args.limit, include_forms=args.include_forms)
    except Exception as e:
        log_error(f"[CLI] Filing document ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

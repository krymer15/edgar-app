# scripts/crawler_idx/run_daily_documents_ingest.py

"""
Run SGML filing document ingestion from crawler.idx-derived metadata.

Usage:
    python scripts/crawler_idx/run_daily_documents_ingest.py --date 2024-12-20 --limit 50
"""

import os, sys
import argparse
from datetime import datetime

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from utils.report_logger import log_info, log_error
from utils.cache_manager import clear_sgml_cache

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
    parser.add_argument("--use_cache", action="store_true", help="Enable SGML caching")
    parser.add_argument("--clear_cache", action="store_true", help="Delete SGML cache before running")
    
    # Optional placeholder for --skip_forms, not yet implemented
    # parser.add_argument("--skip_forms", nargs="+", help="Form types to skip")

    args = parser.parse_args()

    orchestrator = FilingDocumentsOrchestrator(use_cache=args.use_cache)
    try:
        log_info(f"[CLI] Starting filing document ingestion for {args.date} (limit={args.limit}, cache={args.use_cache})")
        if args.clear_cache:
            deleted = clear_sgml_cache()
            log_info(f"🧹 Cleared {deleted} SGML cache files")

        orchestrator.run(target_date=args.date, limit=args.limit)
    except Exception as e:
        log_error(f"[CLI] Filing document ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

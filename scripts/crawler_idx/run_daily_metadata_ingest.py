# scripts/crawler_idx/run_daily_metadata_ingest.py

"""
Run metadata ingestion for a single or multiple past dates from crawler.idx
Usage:
    python scripts/crawler_idx/run_daily_metadata_ingest.py --date 2024-12-20
    python scripts/crawler_idx/run_daily_metadata_ingest.py --backfill 5
"""

import os, sys
import argparse
from datetime import datetime, timedelta

# === [Universal Header] Add project root to path ===
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator
from utils.report_logger import log_info, log_error

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD.")


def main():
    parser = argparse.ArgumentParser(description="Run crawler.idx metadata ingestion.")

    parser.add_argument("--date", type=validate_date, help="Target date to ingest (YYYY-MM-DD)")
    parser.add_argument("--backfill", type=int, help="Ingest N days backwards from today (e.g., 7)")
    parser.add_argument("--limit", type=int, help="Limit number of records per day (for testing)")

    args = parser.parse_args()
    orchestrator = FilingMetadataOrchestrator()

    try:
        if args.backfill:
            today = datetime.utcnow().date()
            for i in range(args.backfill):
                target_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                log_info(f"[CLI] Backfill day {i + 1} of {args.backfill}: {target_date}")
                orchestrator.run(date_str=target_date, limit=args.limit)
        elif args.date:
            orchestrator.run(date_str=args.date, limit=args.limit)
        else:
            log_error("Must specify either --date or --backfill.")
            sys.exit(1)

    except Exception as e:
        log_error(f"[CLI] Ingestion failed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
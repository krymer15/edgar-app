# scripts/crawler_idx/run_daily_pipeline_ingest.py

"""
Run full daily ingestion: metadata → document index → SGML .txt download.

Usage:
    python scripts/crawler_idx/run_daily_pipeline_ingest.py --date 2025-05-12 --limit 100
    python scripts/crawler_idx/run_daily_pipeline_ingest.py --date 2025-05-12 --no_cache
"""

import argparse
import sys, os
from datetime import datetime

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionPipeline
from downloaders.sgml_downloader import SgmlDownloader
from utils.report_logger import log_info, log_error
from utils.filing_calendar import is_valid_filing_day

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD.")


def main():
    parser = argparse.ArgumentParser(description="Run full daily ingestion (metadata + docs + SGML .txt)")
    parser.add_argument("--date", type=validate_date, required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Max records to process per stage")
    parser.add_argument("--no_cache", action="store_true", help="Disable SGML cache usage")

    args = parser.parse_args()

    target_date_obj = datetime.strptime(args.date, "%Y-%m-%d").date()
    if not is_valid_filing_day(target_date_obj):
        log_info(f"[CLI] {args.date} is not a valid SEC filing day. Skipping.")
        sys.exit(0)

    try:
        log_info(f"[CLI] 🔁 Launching DailyIngestionPipeline for {args.date} (limit={args.limit}, cache={not args.no_cache})")
        pipeline = DailyIngestionPipeline(use_cache=not args.no_cache)
        pipeline.run(target_date=args.date, limit=args.limit)
    except Exception as e:
        log_error(f"[CLI] Daily pipeline failed: {e}")
        sys.exit(1)

def test_pipeline_avoids_redundant_sgml_download(monkeypatch):
    call_counter = {"count": 0}

    def mocked_download_html(self, url):
        call_counter["count"] += 1
        return "test SGML content"

    monkeypatch.setattr(SgmlDownloader, "download_html", mocked_download_html)

    pipeline = DailyIngestionPipeline(use_cache=True)
    pipeline.run(target_date="2025-05-12", limit=1)

    assert call_counter["count"] == 1, "SGML downloaded more than once!"


if __name__ == "__main__":
    main()

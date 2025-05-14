# scripts/run_daily_ingestion.py

import sys, os

# Insert project root into sys.path
try:
    from utils.get_project_root import get_project_root
    sys.path.insert(0, get_project_root())
except ImportError:
    # Fallback if the utility is unavailable
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionOrchestrator
from config.config_loader import ConfigLoader
from utils.report_logger import log_info
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Run full daily ingestion (metadata + documents).")
    parser.add_argument("--date", required=True, help="Target filing date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=100, help="Limit number of filings to process")
    parser.add_argument("--skip_meta", action="store_true", help="Skip metadata ingestion step")
    parser.add_argument("--skip_docs", action="store_true", help="Skip document parsing step")
    args = parser.parse_args()

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    config = ConfigLoader.load_config()
    log_info(f"Running full ingestion for {args.date}")

    user_agent = config.get("sec_downloader", {}).get("user_agent", "SafeHarborApp/1.0")
    if "@" not in user_agent:
        raise ValueError(f"Invalid user_agent detected: {user_agent}")
    orchestrator = DailyIngestionOrchestrator(user_agent=user_agent)
    orchestrator.run(date_str=args.date, skip_meta=args.skip_meta, skip_docs=args.skip_docs, limit=args.limit)

if __name__ == "__main__":
    main()

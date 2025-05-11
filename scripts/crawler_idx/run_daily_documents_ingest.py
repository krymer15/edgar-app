# scripts/run_daily_documents_ingest.py

import argparse
from orchestrators.filing_documents_orchestrator import FilingDocumentsOrchestrator
from config.config_loader import ConfigLoader
from utils.report_logger import log_info

def main():
    parser = argparse.ArgumentParser(description="Ingest SGML documents for a specific date.")
    parser.add_argument("--date", required=True, help="Target filing date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=100, help="Limit number of filings to process")
    args = parser.parse_args()

    config = ConfigLoader.load_config()
    log_info(f"🚀 Running document ingestion for {args.date}")

    # Note: Currently the orchestrator does NOT use date filtering yet, only --limit
    orchestrator = FilingDocumentsOrchestrator(limit=args.limit)
    orchestrator.orchestrate()

if __name__ == "__main__":
    main()

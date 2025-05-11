# CLI Testing - Developer Utility Only
'''
Runs pipeline (orchestrator) based on either submissions API or daily index crawler.idx
'''

# scripts/ingest_from_source.py

import argparse
import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Setup sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Imports (make sure these modules are ready)
from collectors.submissions_api.submissions_collector import SubmissionsCollector
from collectors.daily_index_collector import DailyIndexCollector
from downloaders.sec_downloader import SECDownloader
from writers.daily_index_writer import DailyIndexWriter
from parsers.index_page_parser import IndexPageParser
from archive.writers.filing_writer import FilingWriter 
from orchestrators.submissions_api.submissions_ingestion_orchestrator import SubmissionsIngestionOrchestrator
from orchestrators.daily_index_orchestrator import DailyIndexOrchestrator
from utils.ticker_cik_mapper import TickerCIKMapper
from config.config_loader import ConfigLoader
from utils.get_project_root import get_project_root
from services.metadata_fetcher import MetadataFetcher

config = ConfigLoader.load_config()
DATABASE_URL = config["database"]["url"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

def main():
    parser = argparse.ArgumentParser(description="Ingest filings from different SEC sources.")
    parser.add_argument("--source", required=True, choices=["submissions", "daily_index"], help="Choose ingestion source")
    parser.add_argument("--cik", required=False, help="Company CIK (10-digit padded)")
    parser.add_argument("--ticker", required=False, help="Company ticker (will map to CIK)")
    parser.add_argument("--date", required=False, help="Date for daily index ingestion (format: YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of filings to process.")
    args = parser.parse_args()

    company = os.getenv("EDGAR_COMPANY_NAME", "SafeHarborAI")
    email = os.getenv("EDGAR_EMAIL", "kris@safeharborstocks.com")
    user_agent = f"{company}/1.0 ({email})"

    if args.source == "submissions":
        if not args.cik and not args.ticker:
            raise ValueError("Must provide --cik or --ticker for submissions ingestion.")

        # Map ticker to CIK if needed
        cik = args.cik
        if args.ticker:
            mapper = TickerCIKMapper()
            cik = mapper.get_cik(args.ticker)

        print(f"🔹 Launching Submissions Ingestion for CIK: {cik}")

        # Setup components
        collector = SubmissionsCollector(user_agent=user_agent)
        downloader = SECDownloader(user_agent=user_agent)
        writer = FilingWriter()  # You may need to implement this or stub for now

        # Orchestrate
        orchestrator = SubmissionsIngestionOrchestrator(
            collector=collector,
            downloader=downloader,
            writer=writer,
            forms_filter=["8-K", "10-K", "10-Q"]  # Optional: restrict forms if desired
        )
        orchestrator.orchestrate(cik)

    elif args.source == "daily_index":
        if not args.date:
            raise ValueError("Must provide --date for daily index ingestion (format: YYYY-MM-DD).")

        print(f"🔹 Launching Daily Index Ingestion for Date: {args.date}")

        # Setup components
        collector = DailyIndexCollector(user_agent=user_agent)
        writer = DailyIndexWriter(db_session=db_session) # write metadata
        parser = IndexPageParser
        fetcher = MetadataFetcher(db_session, source="daily_index")
        downloader = SECDownloader(user_agent=user_agent) 
        content_parser = IndexPageParser() 
        content_writer = FilingWriter()  

        orchestrator = DailyIndexOrchestrator(
            collector=collector,
            parser=parser,
            writer=writer,
            fetcher=fetcher,
            downloader=downloader,
            content_parser=content_parser,
            content_writer=content_writer
        )

        orchestrator.orchestrate(date=args.date, limit=args.limit)

if __name__ == "__main__":
    main()

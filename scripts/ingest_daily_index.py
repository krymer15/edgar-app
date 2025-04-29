# scripts/ingest_daily_index.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.base import Base
from dotenv import load_dotenv
from utils.get_project_root import get_project_root

# Import your modules
from collectors.daily_index_collector import DailyIndexCollector
from parsers.daily_index_parser import DailyIndexParser
from writers.daily_index_writer import DailyIndexWriter
from services.metadata_fetcher import MetadataFetcher
from downloaders.daily_index_downloader import DailyIndexDownloader
from parsers.daily_index_parser import FilingParser
from writers.daily_index_writer import FilingWriter
from orchestrators.daily_index_orchestrator import DailyIndexOrchestrator

# Load environment variables
dotenv_path = os.path.join(get_project_root(), ".env")
load_dotenv(dotenv_path)
DATABASE_URL = os.getenv("DATABASE_URL")

# Database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

collector = DailyIndexCollector()
parser = DailyIndexParser()
writer = DailyIndexWriter()

fetcher = MetadataFetcher(db_session)
downloader = DailyIndexDownloader()
content_parser = FilingParser()
content_writer = FilingWriter()

orchestrator = DailyIndexOrchestrator(
    collector, parser, writer,
    fetcher, downloader, content_parser, content_writer
)

if __name__ == "__main__":
    orchestrator.orchestrate_metadata_ingestion(date="2025-04-26")
    orchestrator.orchestrate_content_ingestion(since_date="2025-04-01")

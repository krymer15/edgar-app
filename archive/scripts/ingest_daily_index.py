# scripts/ingest_daily_index.py
# DEPRECATED: Replaced by `ingest_sgml_batch_from_idx.py`

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.base import Base
from utils.config_loader import ConfigLoader
from utils.get_project_root import get_project_root

# Import your modules
from collectors.daily_index_collector import DailyIndexCollector
from writers.daily_index_writer import DailyIndexWriter
from services.metadata_fetcher import MetadataFetcher
from downloaders.daily_index_downloader import DailyIndexDownloader
from writers.daily_index_writer import FilingWriter
from orchestrators.daily_index_orchestrator import DailyIndexOrchestrator
from parsers.index_page_parser import IndexPageParser

config = ConfigLoader.load_config()
DATABASE_URL = config["database"]["url"]

# Database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

collector = DailyIndexCollector()
writer = DailyIndexWriter()
fetcher = MetadataFetcher(db_session)
downloader = DailyIndexDownloader()
content_parser = IndexPageParser()
content_writer = FilingWriter()

orchestrator = DailyIndexOrchestrator(
    collector, writer,
    fetcher, downloader, content_parser, content_writer
)

if __name__ == "__main__":
    orchestrator.orchestrate_metadata_ingestion(date="2025-04-26")
    orchestrator.orchestrate_content_ingestion(since_date="2025-04-01")

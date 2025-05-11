# orchestrators/filing_documents_orchestrator.py

# Parses SGML .txt to populate filing_documents

from orchestrators.base_orchestrator import BaseOrchestrator
from collectors.crawler_idx.filing_documents_collector import FilingDocumentsCollector
from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter
from models.database import get_db_session
from config.config_loader import ConfigLoader
from utils.report_logger import log_info, log_warn

class FilingDocumentsOrchestrator(BaseOrchestrator):
    def __init__(self):
        config = ConfigLoader.load_config()
        self.user_agent = config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        self.db_session = get_db_session()
        self.collector = FilingDocumentsCollector(db_session=self.db_session, user_agent=self.user_agent)
        self.writer = FilingDocumentsWriter(db_session=self.db_session)

    def orchestrate(self, target_date: str, limit: int = None):
        try:
            documents = self.collector.collect(target_date)
            if limit:
                documents = documents[:limit]
            log_info(f"[DOCS] Collected {len(documents)} filing documents for {target_date}")
            self.writer.write_documents(documents)
        except Exception as e:
            log_warn(f"[DOCS] Error during orchestrate(): {e}")
            raise

    def run(self, target_date: str, limit: int = None):
        log_info(f"[DOCS] Starting document ingestion for {target_date}")
        self.orchestrate(target_date, limit)
        log_info(f"[DOCS] Completed document ingestion for {target_date}")
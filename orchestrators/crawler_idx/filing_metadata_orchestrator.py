# orchestrators/filing_metadata_orchestrator.py

# Collects and writes filing_metadata from crawler.idx

from orchestrators.base_orchestrator import BaseOrchestrator
from collectors.crawler_idx.filing_metadata_collector import FilingMetadataCollector
from writers.crawler_idx.filing_metadata_writer import FilingMetadataWriter
from config.config_loader import ConfigLoader
from utils.report_logger import log_info, log_warn
from models.dataclasses.filing_metadata import FilingMetadata

class FilingMetadataOrchestrator(BaseOrchestrator):
    def __init__(self):
        config = ConfigLoader.load_config()
        user_agent = config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        self.collector = FilingMetadataCollector(user_agent=user_agent)
        self.writer = FilingMetadataWriter()

    def orchestrate(self, date_str: str, limit: int = None, include_forms: list[str] = None):
        try:
            parsed_records: list[FilingMetadata] = self.collector.collect(date_str, include_forms=include_forms)
            if limit:
                parsed_records = parsed_records[:limit]
            log_info(f"[META] Collected {len(parsed_records)} filing metadata records for {date_str}")
            self.writer.upsert_many(parsed_records)
        except Exception as e:
            log_warn(f"[META] Error during orchestrate(): {e}")
            raise

    def run(self, date_str: str, limit: int = None, include_forms: list[str] = None):
        log_info(f"[META] Starting metadata ingestion for {date_str}")
        self.orchestrate(date_str, limit)
        log_info(f"[META] Completed metadata ingestion for {date_str}")

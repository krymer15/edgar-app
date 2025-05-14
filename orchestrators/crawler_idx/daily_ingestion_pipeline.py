# orchestrators/crawler_idx/daily_ingestion_pipeline.py

from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator
from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator
from downloaders.sgml_downloader import SgmlDownloader
from utils.report_logger import log_info
from config.config_loader import ConfigLoader
from models.database import get_db_session

class DailyIngestionPipeline:
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.config = ConfigLoader.load_config()
        self.user_agent = self.config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        self.meta_orchestrator = FilingMetadataOrchestrator()

        # Shared downloader instance of SgmlDownloader across Pipelines 2 and 3 to ensure sharing of `memory_cache` to avoid double downloads or writes of raw SGML files.
        self.sgml_downloader = SgmlDownloader(
            user_agent="SafeHarborBot/1.0",
            use_cache=use_cache
        )

        self.docs_orchestrator = FilingDocumentsOrchestrator(
            use_cache=use_cache,
            write_cache=False,
            downloader=self.sgml_downloader
        )

        self.sgml_orchestrator = SgmlDiskOrchestrator(
            use_cache=False,
            write_cache=False,
            downloader=self.sgml_downloader
        )

    def run(self, target_date: str, limit: int = None):
        log_info(f"[META] Starting filing metadata ingestion for {target_date}")
        self.meta_orchestrator.run(date_str=target_date, limit=limit)

        log_info(f"[DOCS] Starting document indexing for {target_date}")
        self.docs_orchestrator.run(target_date=target_date, limit=limit)

        log_info(f"[SGML] Starting SGML disk download for {target_date}")
        self.sgml_orchestrator.run(target_date=target_date, limit=limit)
        self.sgml_downloader.clear_memory_cache() # Clear memory_cache from after running Pipelines 1 through 3

        log_info(f"[ALL] Daily ingestion pipeline completed for {target_date}")

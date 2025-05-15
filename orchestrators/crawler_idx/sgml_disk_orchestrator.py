# orchestrators/crawler_idx/sgml_disk_orchestrator.py

from orchestrators.base_orchestrator import BaseOrchestrator
from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector
from downloaders.sgml_downloader import SgmlDownloader
from config.config_loader import ConfigLoader
from models.database import get_db_session
from utils.report_logger import log_info

class SgmlDiskOrchestrator(BaseOrchestrator):
    def __init__(self, use_cache: bool = True, write_cache: bool = True, downloader: SgmlDownloader = None):
        self.config = ConfigLoader.load_config()
        self.user_agent = self.config["sec_downloader"]["user_agent"]
        self.use_cache = use_cache
        self.write_cache = write_cache
        self.downloader = downloader

    def orchestrate(self, target_date: str = None, limit: int = None, accession_filters: list[str] = None,
                   include_forms: list[str] = None) -> list[str]:
        # Resolve include_forms from config if not provided
        if include_forms is None and accession_filters is None:
            include_forms = self.config.get("crawler_idx", {}).get("include_forms_default", [])
            
            if include_forms:
                log_info(f"[SGML] Including forms: {include_forms}")
        
        with get_db_session() as session:
            collector = SgmlDiskCollector(
                db_session=session,
                user_agent=self.user_agent,
                use_cache=self.use_cache,
                write_cache=self.write_cache,
                downloader=self.downloader
            )
            written_files = collector.collect(
                target_date=target_date,
                limit=limit,
                accession_filters=accession_filters,
                include_forms=include_forms
            )
            log_info(f"✅ SGML collection complete: {len(written_files)} files written.")
            return written_files

    def run(self, target_date: str = None, limit: int = None, accession_filters: list[str] = None,
           include_forms: list[str] = None):
        log_info(f"[SGML] Starting SGML disk collection for {target_date or '[accession list]'}")
        results = self.orchestrate(
            target_date=target_date, 
            limit=limit, 
            accession_filters=accession_filters,
            include_forms=include_forms
        )
        log_info(f"[SGML] Completed SGML disk collection for {target_date or '[accession list]'} ({len(results)} written)")
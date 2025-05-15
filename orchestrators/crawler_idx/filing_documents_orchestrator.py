# orchestrators/filing_documents_orchestrator.py

# Indexes SGML .txt documents to populate filing_documents table

from orchestrators.base_orchestrator import BaseOrchestrator
from collectors.crawler_idx.filing_documents_collector import FilingDocumentsCollector
from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter
from downloaders.sgml_downloader import SgmlDownloader
from models.database import get_db_session
from config.config_loader import ConfigLoader
from utils.report_logger import log_info, log_warn

class FilingDocumentsOrchestrator(BaseOrchestrator):
    def __init__(self, use_cache: bool = True, write_cache: bool = True, downloader: SgmlDownloader = None):
        config = ConfigLoader.load_config()
        self.user_agent = config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        self.db_session = get_db_session()
        self.collector = FilingDocumentsCollector(
            db_session=self.db_session, 
            user_agent=self.user_agent,
            use_cache=use_cache,
            write_cache=write_cache,
            downloader=downloader
            )
        self.writer = FilingDocumentsWriter(db_session=self.db_session)
        self.config = config

    def orchestrate(self, target_date: str = None, limit: int = None, accession_filters: list[str] = None, 
                    include_forms: list[str] = None):
        # Resolve include_forms from config if not provided
        if include_forms is None and accession_filters is None:
            include_forms = self.config.get("crawler_idx", {}).get("include_forms_default", [])
            
            if include_forms:
                log_info(f"[DOCS] Including forms: {include_forms}")
        
        try:
            documents = self.collector.collect(
                target_date=target_date,
                limit=limit,
                accession_filters=accession_filters,
                include_forms=include_forms
            )

            # Optional safeguard if limit was only passed but not enforced inside collector
            if limit and not accession_filters:
                documents = documents[:limit]

            if accession_filters:
                log_info(f"[DOCS] Indexed {len(documents)} documents filtered by {len(accession_filters)} accession(s)")
            else:
                log_info(f"[DOCS] Indexed {len(documents)} filing document records for {target_date}")

            self.writer.write_documents(documents)

        except Exception as e:
            log_warn(f"[DOCS] Error during orchestrate(): {e}")
            raise

    def run(self, target_date: str = None, limit: int = None, accession_filters: list[str] = None,
            include_forms: list[str] = None):
        log_info(f"[DOCS] Starting SGML indexing for {target_date or '[accession list]'}")
        self.orchestrate(
            target_date=target_date, 
            limit=limit, 
            accession_filters=accession_filters,
            include_forms=include_forms
        )
        log_info(f"[DOCS] Completed SGML indexing for {target_date or '[accession list]'}")
# orchestrators/crawler_idx/daily_ingestion_pipeline.py

from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator
from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator
from downloaders.sgml_downloader import SgmlDownloader
from utils.report_logger import log_info
from config.config_loader import ConfigLoader
from models.database import get_db_session
from models.orm_models.filing_metadata import FilingMetadata

class DailyIngestionPipeline:
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.config = ConfigLoader.load_config()
        self.user_agent = self.config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        self.meta_orchestrator = FilingMetadataOrchestrator()

        # Shared downloader instance of SgmlDownloader across Pipelines 2 and 3 to ensure sharing of `memory_cache` to avoid double downloads or writes of raw SGML files.
        self.sgml_downloader = SgmlDownloader(
            user_agent=self.user_agent,
            use_cache=False
        )

        self.docs_orchestrator = FilingDocumentsOrchestrator(
            use_cache=False,
            write_cache=False,
            downloader=self.sgml_downloader
        )

        self.sgml_orchestrator = SgmlDiskOrchestrator(
            use_cache=False,
            write_cache=False,
            downloader=self.sgml_downloader
        )

    def run(self, target_date: str, limit: int = None, include_forms: list[str] = None):
        # Resolve include_forms from config if not provided
        if include_forms is None:
            include_forms = self.config.get("crawler_idx", {}).get("include_forms_default", [])
        
        if include_forms:
            log_info(f"[META] Including forms: {include_forms}")
        
        # === Pipeline 1: FilingMetadata ===
        log_info(f"[META] Starting filing metadata ingestion for {target_date}")
        self.meta_orchestrator.run(date_str=target_date, limit=limit, include_forms=include_forms)

        # === Lookup accession numbers just written ===
        with get_db_session() as session:
            query = session.query(FilingMetadata.accession_number)\
                .filter(FilingMetadata.filing_date == target_date)
            
            # Apply form type filter if specified
            if include_forms:
                query = query.filter(FilingMetadata.form_type.in_(include_forms))
            
            if limit:
                query = query.limit(limit)

            accession_results = query.all()
            accession_filters = [a[0] for a in accession_results]

        if not accession_filters:
            log_info(f"[META] No filings ingested for {target_date} (limit={limit}). Skipping downstream steps.")
            return

        # === Pipeline 2: FilingDocuments (SGML Index) ===
        log_info(f"[DOCS] Starting document indexing for {target_date}")
        self.docs_orchestrator.run(target_date=target_date, accession_filters=accession_filters)

        # === Pipeline 3: SGML Disk Writer ===
        log_info(f"[SGML] Starting SGML disk download for {target_date}")
        self.sgml_orchestrator.run(target_date=target_date, accession_filters=accession_filters)

        # Clear in-memory SGML cache to prevent memory leaks
        self.sgml_downloader.clear_memory_cache()

        log_info(f"[ALL] Daily ingestion pipeline completed for {target_date}")

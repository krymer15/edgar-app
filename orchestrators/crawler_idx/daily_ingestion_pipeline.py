# orchestrators/crawler_idx/daily_ingestion_pipeline.py

from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator
from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator
from orchestrators.forms.form4_orchestrator import Form4Orchestrator
from parsers.sgml.indexers.sgml_indexer_factory import SgmlIndexerFactory
from downloaders.sgml_downloader import SgmlDownloader
from utils.report_logger import log_info, log_warn, log_error
from utils.job_tracker import create_job, get_job_progress, update_batch_status, update_record_status
from config.config_loader import ConfigLoader
from models.database import get_db_session
from models.orm_models.filing_metadata import FilingMetadata
from models.orm_models.filing_document_orm import FilingDocumentORM
from datetime import datetime
import traceback
from sqlalchemy import select, inspect

class DailyIngestionPipeline:
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.config = ConfigLoader.load_config()
        self.user_agent = self.config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        self.meta_orchestrator = FilingMetadataOrchestrator()

        # Shared downloader instance of SgmlDownloader across Pipelines 2 and 3
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

        # Create Form4Orchestrator with shared downloader
        self.form4_orchestrator = Form4Orchestrator(
            use_cache=use_cache,
            write_cache=False,  # DailyIngestionPipeline convention
            downloader=self.sgml_downloader  # Share the downloader
        )

        # Check for required tables
        self.form4_processing_enabled = self._check_database_schema()

    def _check_database_schema(self):
        """Check if the database schema includes required Form 4 tables."""
        try:
            with get_db_session() as session:
                inspector = inspect(session.bind)

                required_tables = ["entities", "form4_filings", "form4_relationships", "form4_transactions"]
                existing_tables = inspector.get_table_names()

                missing_tables = [table for table in required_tables if table not in existing_tables]

                if missing_tables:
                    log_warn(f"Missing Form 4 tables: {missing_tables}. Form 4 processing will be skipped.")
                    return False
                return True
        except Exception as e:
            log_warn(f"Error checking database schema: {str(e)}. Form 4 processing will be disabled.")
            return False

    def run(self, target_date: str, limit: int = None, include_forms: list[str] = None, 
            retry_failed: bool = False, job_id: str = None, process_only: list[str] = None):
        """
        Run the daily ingestion pipeline with robust processing and status tracking.
        
        Args:
            target_date: Target date in YYYY-MM-DD format
            limit: Maximum number of records to process
            include_forms: List of form types to include
            retry_failed: Whether to retry failed records
            job_id: Optional job ID for tracking related runs (will be created if not provided)
            process_only: Optional list of specific accession numbers to process
        """
        # Resolve include_forms from config if not provided
        if include_forms is None:
            include_forms = self.config.get("crawler_idx", {}).get("include_forms_default", [])
        
        if include_forms:
            log_info(f"[META] Including forms: {include_forms}")
        
        # Create or use job ID for tracking
        if not job_id:
            job_id = create_job(target_date, f"Daily ingestion for {target_date}")
            log_info(f"[META] Created new job {job_id} for date {target_date}")
        else:
            log_info(f"[META] Using existing job {job_id}")
            job_progress = get_job_progress(job_id)
            log_info(f"[META] Job progress: {job_progress['completed']}/{job_progress['total']} completed, {job_progress['failed']} failed")
        
        # === Pipeline 1: FilingMetadata - Always run this to ensure we have all metadata ===
        if not process_only:  # Skip metadata collection if specific accessions provided
            log_info(f"[META] Starting filing metadata ingestion for {target_date}")
            # Apply limit to metadata collection if provided
            self.meta_orchestrator.run(date_str=target_date, limit=limit, include_forms=include_forms)

        # === Find records to process ===
        with get_db_session() as session:
            # Start building the query
            query = session.query(FilingMetadata)
            
            if process_only:
                # Process specific accession numbers only
                query = query.filter(FilingMetadata.accession_number.in_(process_only))
            else:
                # Apply date filter
                query = query.filter(FilingMetadata.filing_date == target_date)
                
                # Apply form type filter if specified
                if include_forms:
                    query = query.filter(FilingMetadata.form_type.in_(include_forms))
                
                # Subquery to find already processed accession numbers
                if not retry_failed:
                    processed_accessions_query = select(FilingDocumentORM.accession_number)\
                        .distinct()
                    processed_accessions = session.execute(processed_accessions_query).scalars().all()
                    if processed_accessions:
                        query = query.filter(~FilingMetadata.accession_number.in_(processed_accessions))
                
                # Apply status filter based on retry_failed flag
                if retry_failed:
                    query = query.filter(FilingMetadata.processing_status == 'failed')
                else:
                    # Include records with NULL or 'pending' status
                    query = query.filter(
                        (FilingMetadata.processing_status.is_(None)) | 
                        (FilingMetadata.processing_status == 'pending')
                    )
            
            # Add consistent ordering and apply limit
            query = query.order_by(FilingMetadata.accession_number)
            
            if limit:
                query = query.limit(limit)
            
            # Execute query to get records
            records_to_process = query.all()
            accession_filters = [r.accession_number for r in records_to_process]
            
            log_info(f"[META] Selected {len(accession_filters)} records to process: {accession_filters}")
            
            # Update status to 'processing' and set job_id for selected records
            for record in records_to_process:
                record.processing_status = 'processing'
                record.processing_started_at = datetime.now()
                record.job_id = job_id
                record.last_updated_by = f"DailyIngestionPipeline-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            session.commit()

        if not accession_filters:
            log_info(f"[META] No records to process for {target_date} (limit={limit}). Skipping downstream steps.")
            return

        # === Process each record individually with error handling ===
        successfully_processed = []
        failed_records = []
        
        for accession_number in accession_filters:
            try:
                log_info(f"[PIPELINE] Processing {accession_number}")

                # Get the filing metadata record
                with get_db_session() as session:
                    filing_record = session.query(FilingMetadata).filter_by(
                        accession_number=accession_number
                    ).first()

                    if not filing_record:
                        log_error(f"[ERROR] Filing metadata not found for {accession_number}")
                        continue

                # === Pipeline 2: FilingDocuments (SGML Index) ===
                log_info(f"[DOCS] Document indexing for {accession_number}")
                self.docs_orchestrator.run(accession_filters=[accession_number])

                # === Pipeline 3: SGML Disk Writer ===
                log_info(f"[SGML] SGML disk download for {accession_number}")
                self.sgml_orchestrator.run(accession_filters=[accession_number])

                # === Form-Specific Processing ===
                # Form 4 specialized processing
                if filing_record.form_type.strip().upper() in ["4", "FORM 4", "4/A", "FORM 4/A"]:
                    log_info(f"[FORM4] Processing Form 4 data for {accession_number}")

                    # Use the dedicated Form4Orchestrator
                    form4_result = self.form4_orchestrator.run(
                        accession_filters=[accession_number],
                        reprocess=True  # Process even if already exists
                    )

                    if form4_result and form4_result.get("succeeded", 0) > 0:
                        log_info(f"[FORM4] Successfully processed Form 4 data for {accession_number}")
                    else:
                        log_warn(f"[FORM4] Failed to process Form 4 data for {accession_number}")
                        # Note: We don't fail the entire pipeline if just the Form 4 specialized
                        # processing fails, as the general document indexing succeeded

                # Mark as successfully processed
                update_record_status(accession_number, 'completed')
                successfully_processed.append(accession_number)

            except Exception as e:
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                log_error(f"[ERROR] Failed to process {accession_number}: {error_msg}")
                update_record_status(accession_number, 'failed', error_msg)
                failed_records.append((accession_number, error_msg))

        # Clear in-memory SGML cache to prevent memory leaks
        self.sgml_downloader.clear_memory_cache()

        # Log summary
        log_info(f"[ALL] Daily ingestion pipeline completed for {target_date}")
        log_info(f"[SUMMARY] Processed {len(accession_filters)} records:")
        log_info(f"[SUMMARY] - {len(successfully_processed)} succeeded")
        log_info(f"[SUMMARY] - {len(failed_records)} failed")
        
        # Report final job progress
        job_progress = get_job_progress(job_id)
        log_info(f"[JOB] Progress: {job_progress['completed']}/{job_progress['total']} completed ({job_progress['progress_pct']:.1f}%), {job_progress['failed']} failed")
# orchestrators/forms/form4_orchestrator.py

from orchestrators.base_orchestrator import BaseOrchestrator
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from parsers.forms.form4_parser import Form4Parser
from writers.forms.form4_writer import Form4Writer
from writers.shared.raw_file_writer import RawFileWriter
from downloaders.sgml_downloader import SgmlDownloader
from models.database import get_db_session
from models.dataclasses.raw_document import RawDocument
from models.orm_models.filing_metadata import FilingMetadata
from models.orm_models.forms.form4_filing_orm import Form4Filing
from utils.report_logger import log_info, log_warn, log_error
from utils.url_builder import construct_sgml_txt_url
from utils.accession_formatter import format_for_url, format_for_filename, format_for_db
from utils.path_manager import build_raw_filepath_by_type
from config.config_loader import ConfigLoader
from datetime import datetime
import os
import traceback
from typing import List, Optional, Dict, Any

class Form4Orchestrator(BaseOrchestrator):
    """
    Orchestrator for Form 4 filings.

    This orchestrator integrates with the existing daily ingestion pipeline to:
    1. Find Form 4 SGML files (either from Pipeline 3 disk output or in-memory cache)
    2. Parse them using the Form4SgmlIndexer
    3. Write the parsed data to the database using Form4Writer

    It respects the shared downloader pattern of the DailyIngestionPipeline.
    """

    def __init__(self, use_cache: bool = False, write_cache: bool = False, downloader: SgmlDownloader = None):
        """
        Initialize the Form4Orchestrator.

        Args:
            use_cache: Whether to use file-based cache (defaults to False like DailyIngestionPipeline)
            write_cache: Whether to write to file-based cache (defaults to False like DailyIngestionPipeline)
            downloader: Shared SgmlDownloader instance (from DailyIngestionPipeline)
        """
        self.config = ConfigLoader.load_config()
        self.base_data_path = self.config.get("storage", {}).get("base_data_path", "data")
        self.user_agent = self.config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")

        # Respect the same cache configuration as DailyIngestionPipeline
        self.use_cache = use_cache
        self.write_cache = write_cache

        # Use shared downloader if provided, otherwise create a new one
        if downloader:
            self.downloader = downloader
        else:
            self.downloader = SgmlDownloader(
                user_agent=self.user_agent,
                request_delay_seconds=0.1,
                use_cache=self.use_cache
            )

        log_info(f"[FORM4] Initialized with shared downloader: {downloader is not None}")

    def orchestrate(self, target_date: str = None, limit: int = None,
                accession_filters: List[str] = None, reprocess: bool = False,
                write_raw_xml: bool = False) -> Dict[str, Any]:
        """
        Main orchestration method for Form 4 processing.

        Args:
            target_date: Target date in YYYY-MM-DD format (optional)
            limit: Maximum number of records to process (optional)
            accession_filters: List of specific accession numbers to process (optional)
            reprocess: Whether to reprocess records that have already been processed
            write_raw_xml: Whether to write raw XML to disk

        Returns:
            Dictionary with processing results
        """
        log_info(f"[FORM4] Starting Form 4 processing for {target_date or '[accession list]'}")

        # Results tracking
        results = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "failures": []
        }

        # Get filings to process
        with get_db_session() as db_session:
            filings_to_process = self._get_filings_to_process(
                db_session,
                target_date=target_date,
                limit=limit,
                accession_filters=accession_filters,
                reprocess=reprocess
            )

            if not filings_to_process:
                log_info(f"[FORM4] No Form 4 filings found to process")
                return results

            log_info(f"[FORM4] Found {len(filings_to_process)} Form 4 filings to process")
            results["total"] = len(filings_to_process)

            # Create writer instances
            form4_writer = Form4Writer(db_session)
            # Initialize RawFileWriter specifically for XML
            raw_writer = RawFileWriter(file_type="xml") if write_raw_xml else None

            # Process each filing
            for filing in filings_to_process:
                try:
                    results["processed"] += 1
                    log_info(f"[FORM4] Processing filing {filing.accession_number} ({results['processed']}/{results['total']})")

                    # First, try to get SGML from memory cache - most efficient route
                    sgml_content = self._get_sgml_content(filing.cik, filing.accession_number)

                    if not sgml_content:
                        log_error(f"[FORM4] Failed to get SGML content for {filing.accession_number}")
                        results["failed"] += 1
                        results["failures"].append({
                            "accession_number": filing.accession_number,
                            "error": "SGML content not found"
                        })
                        continue

                    # Create and use indexer
                    indexer = Form4SgmlIndexer(filing.cik, filing.accession_number)
                    indexed_data = indexer.index_documents(sgml_content)

                    form4_data = indexed_data.get("form4_data")
                    xml_content = indexed_data.get("xml_content")
                    
                    # Bug 8: Get the issuer CIK from the indexer
                    issuer_cik = indexed_data.get("issuer_cik")
                    if issuer_cik and issuer_cik != filing.cik:
                        log_info(f"[FORM4] Using issuer CIK {issuer_cik} from XML instead of {filing.cik}")

                    if not form4_data:
                        log_error(f"[FORM4] Failed to parse Form 4 data for {filing.accession_number}")
                        results["failed"] += 1
                        results["failures"].append({
                            "accession_number": filing.accession_number,
                            "error": "Failed to parse Form 4 data"
                        })
                        continue

                    # Write raw XML if requested
                    if write_raw_xml and xml_content:
                        # Extract year from filing date
                        filing_year = filing.filing_date.strftime("%Y") if filing.filing_date else datetime.now().strftime("%Y")
                        
                        # Create a RawDocument with the XML content for RawFileWriter
                        xml_filename = f"{format_for_filename(filing.accession_number)}_form4.xml"
                        
                        # Bug 8: Use issuer CIK for both the source URL and the RawDocument
                        # This ensures the file is saved under the correct issuer CIK path
                        use_cik = issuer_cik if issuer_cik else filing.cik
                        
                        source_url = construct_sgml_txt_url(
                            use_cik, 
                            format_for_url(filing.accession_number)
                        )
                        
                        xml_doc = RawDocument(
                            cik=use_cik,  # Bug 8: Use issuer CIK to ensure correct file path construction
                            accession_number=filing.accession_number,  # Keep dashes for path construction
                            form_type=filing.form_type,
                            filing_date=filing.filing_date,
                            content=xml_content,
                            filename=xml_filename,
                            document_type="xml",
                            source_url=source_url,
                            source_type="form4_xml",
                            description=f"Form 4 XML for {filing.accession_number}"
                        )
                        
                        # Use RawFileWriter.write method with RawDocument
                        xml_path = raw_writer.write(xml_doc)
                        log_info(f"[FORM4] Wrote raw XML to {xml_path}")

                    # Write to database
                    form4_orm = form4_writer.write_form4_data(form4_data)

                    if form4_orm:
                        log_info(f"[FORM4] Successfully processed {filing.accession_number}")

                        # Update filing metadata status
                        filing.processing_status = "completed"
                        filing.processing_completed_at = datetime.now()
                        filing.processing_error = None

                        results["succeeded"] += 1
                    else:
                        log_error(f"[FORM4] Failed to write Form 4 data for {filing.accession_number}")

                        # Update filing metadata status
                        filing.processing_status = "failed"
                        filing.processing_error = "Failed to write Form 4 data"

                        results["failed"] += 1
                        results["failures"].append({
                            "accession_number": filing.accession_number,
                            "error": "Failed to write Form 4 data"
                        })

                except Exception as e:
                    error_msg = f"{str(e)}\n{traceback.format_exc()}"
                    log_error(f"[FORM4] Error processing {filing.accession_number}: {error_msg}")

                    # Update filing metadata status
                    filing.processing_status = "failed"
                    filing.processing_error = error_msg

                    results["failed"] += 1
                    results["failures"].append({
                        "accession_number": filing.accession_number,
                        "error": str(e)
                    })

            # Commit any remaining changes
            db_session.commit()

        log_info(
            f"[FORM4] Completed Form 4 processing: {results['succeeded']} succeeded, "
            f"{results['failed']} failed, {results['skipped']} skipped"
        )
        return results


    def run(self, target_date: str = None, limit: int = None,
            accession_filters: List[str] = None, reprocess: bool = False,
            write_raw_xml: bool = False) -> Dict[str, Any]:
        """
        Public run method with additional logging.

        Args:
            target_date: Target date in YYYY-MM-DD format (optional)
            limit: Maximum number of records to process (optional)
            accession_filters: List of specific accession numbers to process (optional)
            reprocess: Whether to reprocess records that have already been processed
            write_raw_xml: Whether to write raw XML to disk

        Returns:
            Dictionary with processing results
        """
        try:
            log_info(f"[FORM4] Starting Form 4 processing run")
            results = self.orchestrate(
                target_date=target_date,
                limit=limit,
                accession_filters=accession_filters,
                reprocess=reprocess,
                write_raw_xml=write_raw_xml
            )
            log_info(f"[FORM4] Completed Form 4 processing run")
            return results
        except Exception as e:
            log_error(f"[FORM4] Run failed: {e}")
            raise

    def _get_filings_to_process(self, db_session, target_date: str = None, limit: int = None,
                                accession_filters: List[str] = None, reprocess: bool = False) -> List[FilingMetadata]:
        """
        Get Form 4 filings to process based on the provided filters.

        Args:
            db_session: Database session
            target_date: Target date in YYYY-MM-DD format (optional)
            limit: Maximum number of records to process (optional)
            accession_filters: List of specific accession numbers to process (optional)
            reprocess: Whether to reprocess records that have already been processed

        Returns:
            List of FilingMetadata objects
        """
        query = db_session.query(FilingMetadata)

        # Apply form type filter (Form 4 and variations like 4/A)
        query = query.filter(FilingMetadata.form_type.in_(["4", "4/A"]))

        # Apply accession filters if provided
        if accession_filters:
            query = query.filter(FilingMetadata.accession_number.in_(accession_filters))

        # Apply date filter if provided
        if target_date:
            query = query.filter(FilingMetadata.filing_date == target_date)

        # Filter out already processed records if not reprocessing
        if not reprocess:
            # Subquery to find accession numbers already in form4_filings
            existing_form4_query = db_session.query(Form4Filing.accession_number)
            existing_accessions = existing_form4_query.all()

            if existing_accessions:
                # Extract accession numbers from tuples
                existing_accessions = [a[0] for a in existing_accessions]
                query = query.filter(~FilingMetadata.accession_number.in_(existing_accessions))

        # Apply limit if provided
        if limit:
            query = query.limit(limit)

        # Execute query
        return query.all()

    def _get_sgml_content(self, cik: str, accession_number: str) -> Optional[str]:
        """
        Get SGML content for a filing using the most efficient source.
        Prioritizes memory cache, then disk cache, then downloading.
        
        This method is responsible for translating between dataclass and string 
        representations as needed by different components.
        
        Bug 8 Fix: This method now tries to extract the issuer CIK from XML content when
        it becomes available, and uses that for URL construction in subsequent operations
        to ensure consistency.

        Args:
            cik: CIK (could be issuer or reporting owner)
            accession_number: Accession number

        Returns:
            String content of the SGML or None if not found
        """
        log_info(f"[FORM4] Getting SGML content for {accession_number}")

        # Try from the shared downloader's memory cache first
        url = construct_sgml_txt_url(cik, format_for_url(accession_number))

        # Check if the downloader has this URL in its memory cache
        if self.downloader.has_in_memory_cache(url):
            log_info(f"[FORM4] Using SGML from memory cache for {accession_number}")
            sgml_content = self.downloader.get_from_memory_cache(url)
            
            # Bug 8: After getting content, try to extract issuer CIK
            xml_start = sgml_content.find("<XML>")
            xml_end = sgml_content.find("</XML>", xml_start) if xml_start != -1 else -1
            issuer_cik = None
            if xml_start != -1 and xml_end != -1:
                xml_content = sgml_content[xml_start+5:xml_end].strip()
                issuer_cik = Form4Parser.extract_issuer_cik_from_xml(xml_content)
            if issuer_cik and issuer_cik != cik:
                log_info(f"[FORM4] Found issuer CIK {issuer_cik} in XML, different from {cik}")
                # If we found a different issuer CIK, check if we should try another URL
                alt_url = construct_sgml_txt_url(issuer_cik, format_for_url(accession_number))
                if alt_url != url and self.downloader.has_in_memory_cache(alt_url):
                    log_info(f"[FORM4] Found alternate URL in cache using issuer CIK {issuer_cik}")
                    return self.downloader.get_from_memory_cache(alt_url)
            
            return sgml_content

        # Next, try from disk if Pipeline 3 has already saved it
        sgml_path = self._get_sgml_file_path(cik, accession_number)
        if os.path.exists(sgml_path):
            log_info(f"[FORM4] Using SGML from disk for {accession_number}")
            with open(sgml_path, 'r', encoding='utf-8', errors='replace') as f:
                sgml_content = f.read()
                
                # Bug 8: Try to extract issuer CIK from the content
                xml_start = sgml_content.find("<XML>")
                xml_end = sgml_content.find("</XML>", xml_start) if xml_start != -1 else -1
                issuer_cik = None
                if xml_start != -1 and xml_end != -1:
                    xml_content = sgml_content[xml_start+5:xml_end].strip()
                    issuer_cik = Form4Parser.extract_issuer_cik_from_xml(xml_content)
                if issuer_cik and issuer_cik != cik:
                    log_info(f"[FORM4] Found issuer CIK {issuer_cik} in XML, different from {cik}")
                    
                    # Check if there's a file under the issuer CIK path
                    alt_path = self._get_sgml_file_path(issuer_cik, accession_number)
                    if os.path.exists(alt_path) and alt_path != sgml_path:
                        log_info(f"[FORM4] Found file at issuer CIK path {alt_path}, using that instead")
                        with open(alt_path, 'r', encoding='utf-8', errors='replace') as f2:
                            return f2.read()
                
                return sgml_content

        # Finally, try to download (this will also update memory cache)
        log_info(f"[FORM4] Downloading SGML for {accession_number}")
        
        # Extract year from accession number (assuming format: 0000123456-YY-123456)
        year = None
        if len(accession_number) >= 10 and '-' in accession_number:
            parts = accession_number.split('-')
            if len(parts) >= 2:
                year_short = parts[1]
                year = f"20{year_short}"  # Assuming all years are 2000+
                
        # Get SgmlTextDocument from downloader
        sgml_doc = self.downloader.download_sgml(cik, accession_number, year)
        
        # Extract string content from the dataclass
        if sgml_doc:
            # Handle either SgmlTextDocument object or string
            if hasattr(sgml_doc, 'content'):
                sgml_content = sgml_doc.content
            else:
                sgml_content = str(sgml_doc)
                
            # Bug 8: Try to extract issuer CIK from content before writing to disk
            xml_start = sgml_content.find("<XML>")
            xml_end = sgml_content.find("</XML>", xml_start) if xml_start != -1 else -1
            issuer_cik = None
            if xml_start != -1 and xml_end != -1:
                xml_content = sgml_content[xml_start+5:xml_end].strip()
                issuer_cik = Form4Parser.extract_issuer_cik_from_xml(xml_content)
            if issuer_cik and issuer_cik != cik:
                log_info(f"[FORM4] Found issuer CIK {issuer_cik} in downloaded XML, different from {cik}")
                
                # Try to download with issuer CIK if it's different
                alt_sgml_doc = self.downloader.download_sgml(issuer_cik, accession_number, year)
                if alt_sgml_doc:
                    if hasattr(alt_sgml_doc, 'content'):
                        new_content = alt_sgml_doc.content
                    else:
                        new_content = str(alt_sgml_doc)
                        
                    if new_content:
                        log_info(f"[FORM4] Successfully downloaded using issuer CIK {issuer_cik}")
                        sgml_content = new_content
                        cik = issuer_cik  # Use issuer CIK for path construction
                
            # For standalone mode, write to disk if requested
            if sgml_content and self.write_cache:
                # Bug 8: Use the correct CIK (original or issuer) for path construction
                sgml_path = self._get_sgml_file_path(cik, accession_number)
                os.makedirs(os.path.dirname(sgml_path), exist_ok=True)
                with open(sgml_path, 'w', encoding='utf-8') as f:
                    f.write(sgml_content)
                log_info(f"[FORM4] Wrote SGML to disk at {sgml_path}")
            
            return sgml_content
        
        return None

    def _get_sgml_file_path(self, cik: str, accession_number: str) -> str:
        """
        Get the path to the SGML file for a given CIK and accession number.

        Args:
            cik: CIK
            accession_number: Accession number

        Returns:
            Path to the SGML file
        """
        # Normalize accession number for path construction
        acc_clean = format_for_filename(accession_number)

        # Construct path based on config and standard pattern
        sgml_path = os.path.join(
            self.base_data_path,
            "sgml",
            cik,
            f"{acc_clean}.txt"
        )

        return sgml_path
        

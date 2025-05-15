# collectors/sgml_disk_collector.py

from typing import List, Optional
import os

from sqlalchemy import cast, Date
from sqlalchemy.orm import Session, joinedload
from models.dataclasses.filing_document_record import FilingDocumentRecord
from models.dataclasses.raw_document import RawDocument
from models.orm_models.filing_document_orm import FilingDocumentORM
from models.orm_models.filing_metadata import FilingMetadata
from downloaders.sgml_downloader import SgmlDownloader
from writers.shared.raw_file_writer import RawFileWriter
from utils.path_manager import build_raw_filepath_by_type
from utils.report_logger import log_info, log_warn

class SgmlDiskCollector:
    def __init__(self, db_session: Session, user_agent: str, use_cache: bool = True, write_cache: bool = True, downloader: SgmlDownloader = None):
        self.db_session = db_session
        self.downloader = downloader or SgmlDownloader(user_agent=user_agent, use_cache=use_cache)
        self.writer = RawFileWriter(file_type="sgml")
        self.write_cache = write_cache

    def collect(
        self, 
        target_date: str = None, 
        limit: int = None, 
        accession_filters: list[str] = None,
        include_forms: Optional[List[str]] = None
    ) -> List[str]:
        """
        Downloads and saves SGML files to disk, optionally filtered by form types.
        
        Args:
            target_date: Target date string in YYYY-MM-DD format
            limit: Maximum number of files to retrieve
            accession_filters: List of specific accession numbers to process
            include_forms: List of form types to include (e.g., ["10-K", "8-K"])
            
        Returns:
            List of filepaths where SGML files were saved
        """
        query = (
            self.db_session.query(FilingDocumentORM)
            .join(FilingDocumentORM.filing)
            .options(joinedload(FilingDocumentORM.filing))
            .filter(FilingDocumentORM.source_type == "sgml")
        )

        if accession_filters:
            query = query.filter(FilingDocumentORM.accession_number.in_(accession_filters))
        elif target_date:
            query = query.filter(FilingMetadata.filing_date == target_date)

            # Apply form type filtering if specified and not using accession filters
            if include_forms:
                log_info(f"[SGML] Filtering SGML files by form types: {include_forms}")
                query = query.filter(FilingMetadata.form_type.in_(include_forms))

        if limit and not accession_filters:
            query = query.limit(limit)

        results = query.all()

        if include_forms:
            log_info(f"[SGML] Processing {len(results)} SGML files for form types: {include_forms}")
        else:
            log_info(f"[SGML] Processing {len(results)} SGML files")

        seen_keys = set()
        written_paths = []

        for record in results:
            try:
                cik = record.cik
                accession = record.accession_number
                form_type = record.filing.form_type
                year = str(record.filing.filing_date.year)
                
                # Skip if already written for this accession number
                key = (cik, accession)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                
                # Step 1: Check if file already exists
                full_path = build_raw_filepath_by_type(
                    file_type="sgml",
                    year=year,
                    cik=cik,
                    form_type=form_type, # FilingMetadata.form_type
                    accession_or_subtype=accession,
                    filename=f"{record.accession_number}.txt", # patch in submission .txt filename
                )

                if os.path.exists(full_path):
                    log_info(f"Already written: {full_path}")
                    continue

                # Step 2: Fetch SGML (cache-aware)
                sgml_doc = self.downloader.download_sgml(
                    cik, 
                    accession,
                    year=year,
                    write_cache=self.write_cache
                )

                # Step 3: Wrap into RawDocument
                raw_doc = RawDocument(
                    accession_number=accession,
                    cik=cik,
                    form_type=record.filing.form_type,
                    document_type=record.document_type,
                    filename=f"{record.accession_number}.txt",
                    source_url=record.source_url or "https://www.sec.gov",
                    source_type=record.source_type or "sgml",
                    content=sgml_doc.content,
                    filing_date=record.filing.filing_date,
                    description=record.description,
                    is_primary=record.is_primary,
                    is_exhibit=record.is_exhibit,
                    is_data_support=record.is_data_support,
                    accessible=record.accessible,
                )

                # Step 4: Write to disk
                path = self.writer.write(raw_doc)
                written_paths.append(path)

            except Exception as e:
                log_warn(f"Failed to process {record.accession_number}: {e}")
                continue

        return written_paths

# collectors/sgml_disk_collector.py

from typing import List
import os

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
    def __init__(self, db_session: Session, user_agent: str, use_cache: bool = True):
        self.db_session = db_session
        self.downloader = SgmlDownloader(user_agent=user_agent, use_cache=use_cache)
        self.writer = RawFileWriter(file_type="sgml")

    def collect(self, target_date: str) -> List[str]:
        results = (
            self.db_session.query(FilingDocumentORM)
            .options(joinedload(FilingDocumentORM.filing))  # assumes back_populates="filing"
            .filter(FilingDocumentORM.source_type == "sgml")
            .all()
        )

        written_paths = []
        for record in results:
            try:
                # Step 1: Check if file already exists
                year = str(record.filing.filing_date.year)
                full_path = build_raw_filepath_by_type(
                    file_type="sgml",
                    year=year,
                    cik=record.cik,
                    form_type=record.document_type,
                    accession_or_subtype=record.accession_number,
                    filename=record.filename,
                )

                if os.path.exists(full_path):
                    log_info(f"⏭️ Already written: {full_path}")
                    continue

                # Step 2: Fetch SGML (cache-aware)
                sgml_doc = self.downloader.download_sgml(record.cik, record.accession_number)

                # Step 3: Wrap into RawDocument
                raw_doc = RawDocument(
                    accession_number=record.accession_number,
                    cik=record.cik,
                    document_type=record.document_type or "10-K",
                    filename=record.filename or "submission.txt",
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
                log_warn(f"⚠️ Failed to process {record.accession_number}: {e}")
                continue

        return written_paths

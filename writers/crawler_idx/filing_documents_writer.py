# writers/filing_documents_writer.py

from sqlalchemy.exc import SQLAlchemyError
from writers.base_writer import BaseWriter
from models.adapters.dataclass_to_orm import convert_filing_doc_to_orm
from models.dataclasses.filing_document_record import FilingDocumentRecord as FilingDocDC
from models.orm_models.filing_document_orm import FilingDocumentORM
from utils.report_logger import log_info, log_warn, log_error

class FilingDocumentsWriter(BaseWriter):
    def write_metadata(self, *args, **kwargs):
        # Not used for this writer
        pass

    def write_content(self, *args, **kwargs):
        # Placeholder for future RawDocument content writing
        pass

    def write_documents(self, documents: list[FilingDocDC]):
        written = 0
        updated = 0
        skipped = 0

        for dc in documents:
            try:
                # Deduplication check by accession_number + document_type + source_url
                existing = self.db_session.query(FilingDocumentORM).filter_by(
                    accession_number=dc.accession_number,
                    document_type=dc.document_type,
                    source_url=dc.source_url
                ).first()

                if existing:
                    # Update only if something changed (minimal update for now)
                    updated_fields = False
                    if existing.description != dc.description:
                        existing.description = dc.description
                        updated_fields = True
                    if existing.accessible != dc.accessible:
                        existing.accessible = dc.accessible
                        updated_fields = True

                    if updated_fields:
                        updated += 1
                        log_info(f"Updated: {repr(dc)}")
                    else:
                        skipped += 1
                        log_info(f"Skipped (unchanged): {dc.accession_number} → {dc.filename or dc.source_url}")
                    continue

                new_doc = convert_filing_doc_to_orm(dc)
                self.db_session.add(new_doc)
                written += 1
                log_info(f"✅ Written: {repr(dc)}")

            except SQLAlchemyError as e:
                self.db_session.rollback()
                log_error(f"DB error processing document {dc.filename or dc.source_url}: {e}")
                continue

        try:
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            log_error(f"Final commit failed: {e}")

        log_info(f"📝 Filing documents — Written: {written}, Updated: {updated}, Skipped: {skipped}")

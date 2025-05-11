# writers/filing_documents_writer.py

from sqlalchemy.exc import SQLAlchemyError
from models.database import SessionLocal
from models.filing_documents import FilingDocument
from utils.report_logger import log_info, log_warn, log_error

class FilingDocumentsWriter:
    def __init__(self):
        self.session = SessionLocal()

    def write_documents(self, documents: list):
        written = 0
        skipped = 0

        for doc in documents:
            try:
                # Check for existing entry to avoid duplicates
                existing = self.session.query(FilingDocument).filter_by(
                    accession_number=doc.accession_number,
                    filename=doc.filename
                ).first()

                if existing:
                    skipped += 1
                    continue

                new_doc = FilingDocument(
                    accession_number=doc.accession_number,
                    cik=doc.cik,
                    document_type=doc.type,
                    filename=doc.filename,
                    description=doc.description,
                    source_url=doc.source_url,
                    source_type=doc.source_type,
                    is_primary=doc.is_primary,
                    is_exhibit=doc.is_exhibit,
                    is_data_support=doc.is_data_support,
                    accessible=doc.accessible
                )

                self.session.add(new_doc)
                written += 1

            except SQLAlchemyError as e:
                self.session.rollback()
                log_error(f"❌ DB error writing {doc.filename}: {e}")
                continue

        try:
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            log_error(f"❌ Final commit failed: {e}")
        finally:
            self.session.close()

        log_info(f"📝 Filing documents written: {written}, skipped: {skipped}")

# writers/filing_metadata_writer.py

from sqlalchemy.exc import SQLAlchemyError
from models.database import SessionLocal
from models.orm_models.filing_metadata import FilingMetadata as FilingMetadataORM
from models.dataclasses.filing_metadata import FilingMetadata as FilingMetadataDC
from models.adapters.dataclass_to_orm import convert_to_orm
from utils.report_logger import log_warn, log_info

class FilingMetadataWriter:
    def __init__(self):
        self.session = SessionLocal()

    def upsert_many(self, records: list[FilingMetadataDC]):
        written = 0
        for record in records:
            try:
                orm_entry = convert_to_orm(record)
                self.session.merge(orm_entry)
                self.session.commit()
                written += 1
            except SQLAlchemyError as e:
                self.session.rollback()
                log_warn(f"[ERROR] Failed to write filing metadata for {record.accession_number}: {e}")
                
        log_info(f"✅ Metadata written: {written}")
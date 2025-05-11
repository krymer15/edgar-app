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
        try:
            for record in records:
                orm_entry = convert_to_orm(record)
                self.session.merge(orm_entry)
                written += 1
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            log_warn(f"[ERROR] Failed to write filing metadata: {e}")
        finally:
            self.session.close()

        log_info(f"✅ Metadata written: {written}")
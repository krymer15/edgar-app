# /writers/daily_index_writer.py

from sqlalchemy.exc import SQLAlchemyError
from models.database import SessionLocal
from models.daily_index_metadata import DailyIndexMetadata
from utils.report_logger import log_warn

class DailyIndexWriter:
    def __init__(self):
        self.session = SessionLocal()

    def write(self, metadata_list: list[dict]):
        try:
            for entry in metadata_list:    
                record = DailyIndexMetadata(**entry)
                self.session.merge(record)
                self.session.commit() # Run inside for loop to avoid SQLAlchemy BULK INSERT
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"[ERROR] Failed to write daily index metadata: {e}")
        finally:
            self.session.close()

# /writers/daily_index_writer.py

from sqlalchemy.exc import SQLAlchemyError
from utils.database import SessionLocal
from models.daily_index_metadata import DailyIndexMetadata

class DailyIndexWriter:
    def __init__(self):
        self.session = SessionLocal()

    def write(self, metadata_list: list[dict]):
        try:
            for entry in metadata_list:
                record = DailyIndexMetadata(**entry)
                self.session.merge(record)

            self.session.commit()
            print(f"✅ {len(metadata_list)} daily index records written to Postgres.")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"[ERROR] Failed to write daily index metadata: {e}")
        finally:
            self.session.close()

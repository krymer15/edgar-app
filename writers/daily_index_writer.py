# writers/daily_index_writer.py

from writers.base_writer import BaseWriter
from models.daily_index_metadata import DailyIndexMetadata
from sqlalchemy.dialects.postgresql import insert

class DailyIndexWriter(BaseWriter):
    def write_metadata(self, metadata_list):
        """Write collected metadata to database with ON CONFLICT DO NOTHING."""
        for metadata in metadata_list:
            stmt = insert(DailyIndexMetadata).values(
                accession_number=metadata["accession_number"],
                cik=metadata["cik"],
                form_type=metadata["form_type"],
                filing_date=metadata["filing_date"],
                filing_url=metadata["filing_url"]
            ).on_conflict_do_nothing(
                index_elements=['accession_number']
            )
            self.db_session.execute(stmt)

        self.db_session.commit()
        print(f"✅ Inserted {len(metadata_list)} filings into daily_index_metadata (skipping duplicates).")

    def write_content(self, parsed_content):
        """(Placeholder) Write parsed filing content to database or file storage."""
        # Not implemented yet — will be used for raw filing storage.
        pass

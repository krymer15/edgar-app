# writers/xml_metadata_writer.py

'''
METADATA LOGGER FUNCTION
call this from both:

- Form4XmlDownloader → log discovered filenames (even skipped)
- Form4XmlOrchestrator → update parsed_successfully when done
'''

from models.xml_metadata import XmlMetadata
from sqlalchemy.exc import SQLAlchemyError
from models.database import SessionLocal
from utils.report_logger import log_info, log_error

def log_xml_metadata(entry: dict):
    session = SessionLocal()
    try:
        # Check for existing record with same accession + filename
        existing = session.query(XmlMetadata).filter_by(
            accession_number=entry["accession_number"],
            filename=entry["filename"]
        ).first()

        if existing:
            # Update fields if already exists
            existing.downloaded = entry.get("downloaded", existing.downloaded)
            existing.parsed_successfully = entry.get("parsed_successfully", existing.parsed_successfully)
            session.commit()
            log_info(f"Updated XML metadata: {entry['accession_number']} - {entry['filename']}")
        else:
            # Remove redundant fields before model instantiation
            filtered = {
                k: v for k, v in entry.items()
                if k in {"accession_number", "filename", "downloaded", "parsed_successfully"}
            }
            record = XmlMetadata(**filtered)
            session.add(record)
            session.commit()
            log_info(f"Inserted XML metadata: {entry['accession_number']} - {entry['filename']}")

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"[ERROR] Failed to log XML metadata: {e}")

    finally:
        session.close()
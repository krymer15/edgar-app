# Writes parsed output (JSON or DB)
# writers/form4_writer.py

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils.database import SessionLocal
from models.form4_filing import Form4Filing
from utils.report_logger import log_info, log_error

class Form4Writer:
    def __init__(self):
        self.session = SessionLocal()

    def write_metadata(self, *args, **kwargs):
        pass  # Optional: implement later if metadata-only use case arises

    def write_content(self, parsed: dict):
        try:
            data = parsed.get("parsed_data", {})

            filing = Form4Filing(
                accession_number=parsed["accession_number"],
                cik=parsed["cik"],
                form_type=parsed.get("form_type", "4"),
                filing_date=parsed["filing_date"],
                issuer=data.get("issuer"),
                reporting_owner=data.get("reporting_owners"),
                non_derivative_transactions=data.get("non_derivative_transactions", []),
                derivative_transactions=data.get("derivative_transactions", []),
            )

            self.session.add(filing)
            self.session.commit()
            log_info(f"Form 4 filing inserted: {parsed['accession_number']}")

        except IntegrityError:
            self.session.rollback()
            log_info(f"Duplicate Form 4 skipped: {parsed['accession_number']}")

        except SQLAlchemyError as e:
            self.session.rollback()
            log_error(f"Failed to insert Form 4: {e}")

    def close(self):
        self.session.close()

# /writers/parsed_sgml_writer.py

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils.database import SessionLocal
from models.parsed_sgml_metadata import ParsedSgmlMetadata
from models.exhibit_metadata import ExhibitMetadata
from utils.report_logger import log_info, log_warn, log_error, append_ingestion_report
from uuid import uuid4

class ParsedSgmlWriter:
    def __init__(self):
        self.session = SessionLocal()

    def write_metadata(self, metadata_dict: dict):
        try:
            if "primary_document_url" in metadata_dict:
                metadata_dict["primary_doc_url"] = metadata_dict.pop("primary_document_url")

            parsed_metadata = ParsedSgmlMetadata(
                accession_number=metadata_dict.get("accession_number"),
                cik=metadata_dict.get("cik"),
                form_type=metadata_dict.get("form_type"),
                filing_date=metadata_dict.get("filing_date"),
                primary_doc_url=metadata_dict.get("primary_doc_url"),
            )

            self.session.add(parsed_metadata)
            self.session.commit()
            log_info("Parsed SGML metadata written to Postgres.")

        except IntegrityError:
            self.session.rollback()
            log_warn(f"Parsed metadata already exists for: {metadata_dict.get('accession_number')}")

        except SQLAlchemyError as e:
            self.session.rollback()
            log_error(f"Failed to write parsed metadata: {e}")

    def write_exhibits(
        self,
        exhibits: list,
        accession_number: str,
        cik: str = "",
        form_type: str = "",
        filing_date=None,
        primary_doc_url: str = "",
        run_id: str = ""
    ):
        try:
            filtered = [ex for ex in exhibits if ex.get("accessible", True) is True]
            written_count = 0
            skipped_count = 0
            new_exhibits = []

            for ex_dict in filtered:
                ex_model = ExhibitMetadata(
                    id=str(uuid4()),
                    accession_number=accession_number,
                    filename=ex_dict.get("filename", ""),
                    description=ex_dict.get("description", ""),
                    type=ex_dict.get("type", ""),
                    accessible=ex_dict.get("accessible", True)
                )

                existing = self.session.query(ExhibitMetadata).filter_by(
                    accession_number=accession_number,
                    filename=ex_model.filename
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                self.session.add(ex_model)
                new_exhibits.append(ex_model)
                written_count += 1

            if new_exhibits:
                self.session.commit()

            skipped_count += len(exhibits) - len(filtered)

            if written_count > 0 or skipped_count > 0:
                append_ingestion_report({
                    "record_type": "exhibit",
                    "accession_number": accession_number,
                    "cik": cik,
                    "form_type": form_type,
                    "filing_date": str(filing_date) if filing_date else "",
                    "exhibits_written": written_count,
                    "exhibits_skipped": skipped_count,
                    "primary_doc_url": primary_doc_url
                }, run_id=run_id)

            log_info(f"Exhibits written: {written_count}, skipped: {skipped_count}")

        except SQLAlchemyError as e:
            self.session.rollback()
            log_error(f"Failed during exhibit write loop: {e}")

    def close(self):
        self.session.close()

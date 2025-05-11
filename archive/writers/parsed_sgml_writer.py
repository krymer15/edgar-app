# Deprecated
# /writers/parsed_sgml_writer.py

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.database import SessionLocal
from models.parsed_sgml_metadata import ParsedSgmlMetadata
from models.exhibit_metadata import ExhibitMetadata
from utils.report_logger import log_info, log_warn, log_error, append_ingestion_report, log_debug
from uuid import uuid4
from datetime import datetime, timezone

class ParsedSgmlWriter:
    def __init__(self):
        self.session = SessionLocal()

    def write_metadata(self, metadata_dict: dict) -> bool:
        accession_number = metadata_dict.get("accession_number")

        # ✅ Pre-check if row already exists
        exists = self.session.query(ParsedSgmlMetadata).filter_by(
            accession_number=accession_number
        ).first()
        if exists:
            log_warn(f"Parsed metadata already exists (pre-check): {accession_number}")
            return True

        try:
            # ✅ Rename only the one key we need to remap
            # 🛑 Do NOT remove cik or filing_date — they're used in the ingestion report
            if "primary_document_url" in metadata_dict:
                metadata_dict["primary_doc_url"] = metadata_dict.pop("primary_document_url")

            parsed_metadata = ParsedSgmlMetadata(
                accession_number=accession_number,
                primary_doc_url=metadata_dict.get("primary_doc_url"),
                form_type=metadata_dict.get("form_type")
            )

            self.session.add(parsed_metadata)
            self.session.commit()
            log_info("Parsed SGML metadata written to Postgres.")

            # 📋 Write to CSV report
            raw_date = str(metadata_dict.get("filing_date") or "")
            log_debug(f"🧪 filing_date used for log filename: {raw_date}")
            try:
                log_date = datetime.strptime(raw_date, "%Y%m%d").date().isoformat() if len(raw_date) == 8 else raw_date
            except Exception:
                log_date = datetime.now(timezone.utc).date().isoformat()

            log_debug(f"[DEBUG] logging report for accession {accession_number}")
            log_debug(f"  cik: {metadata_dict.get('cik')}")
            log_debug(f"  form_type: {metadata_dict.get('form_type')}")
            log_debug(f"  filing_date: {metadata_dict.get('filing_date')}")
            log_debug(f"  primary_doc_url: {metadata_dict.get('primary_doc_url')}")

            append_ingestion_report({
                "record_type": "parsed",
                "accession_number": accession_number,
                "cik": metadata_dict.get("cik") or "(missing)",
                "form_type": metadata_dict.get("form_type", "(in daily_index)"),
                "filing_date": metadata_dict.get("filing_date") or "(missing)",
                "exhibits_written": 0,
                "exhibits_skipped": 0,
                "primary_doc_url": metadata_dict.get("primary_doc_url", "")
            }, log_date=log_date)

            return True

        except SQLAlchemyError as e:
            self.session.rollback()
            log_error(f"Failed to write parsed metadata: {e}")
            return False


    # Note: write_exhibits() does not log exhibit rows to ingestion_report.csv.
    # If needed later, logging can be added using record_type='exhibit' and log_date=filing_date.
    def write_exhibits(
        self,
        exhibits: list,
        accession_number: str,
        cik: str = "",
        form_type: str = "",
        filing_date=None,
        primary_doc_url: str = ""
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

            log_info(f"Exhibits written: {written_count}, skipped: {skipped_count}")

        except SQLAlchemyError as e:
            self.session.rollback()
            log_error(f"Failed during exhibit write loop: {e}")

    def close(self):
        self.session.close()

import os
from dataclasses import asdict
from utils.path_manager import build_raw_filepath, build_cleaned_filepath
from utils.report_logger import log_info, log_error

class FilingFileWriter:
    def __init__(self, output_type: str = "raw"):
        """
        output_type: "raw" or "cleaned"
        """
        self.output_type = output_type

    def write(self, filing_doc) -> str:
        """
        Write content of a FilingDocument or DownloadedDocument to disk.

        Args:
            filing_doc (FilingDocument or DownloadedDocument): Must contain
                .content, .filename, .accession_number, .cik, .form_type, .filing_date

        Returns:
            str: Full path of the written file
        """
        if not hasattr(filing_doc, "content") or not filing_doc.content:
            raise ValueError("Filing document missing `.content` field.")

        try:
            year = filing_doc.filing_date[:4]
            path_builder = build_raw_filepath if self.output_type == "raw" else build_cleaned_filepath

            full_path = path_builder(
                year=year,
                cik=filing_doc.cik,
                form_type=filing_doc.form_type,
                accession_or_subtype=filing_doc.accession_number,
                filename=filing_doc.filename
            )

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(filing_doc.content)

            log_info(f"📄 Saved filing to disk at {full_path}")
            return full_path

        except Exception as e:
            log_error(f"❌ Failed to write filing content: {e}")
            raise

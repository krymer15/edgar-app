import os
from models.dataclasses.raw_document import RawDocument
from utils.path_manager import build_raw_filepath_by_type
from utils.report_logger import log_info, log_error

class RawFileWriter:
    """
    Generic writer for raw files (SGML, HTML index, XML, etc).
    Accepts a RawDocument and writes its `.content` to disk.
    """

    def __init__(self, file_type: str = "sgml"):
        if file_type not in {"sgml", "html_index", "exhibits", "xml"}:
            raise ValueError(f"Unsupported file_type: {file_type}")
        self.file_type = file_type

    def write(self, raw_doc: RawDocument) -> str:
        if not raw_doc.content:
            raise ValueError("RawDocument is missing `.content`")

        try:
            year = str(raw_doc.filing_date.year)
            path = build_raw_filepath_by_type(
                file_type=self.file_type,
                year=year,
                cik=raw_doc.cik,
                form_type=raw_doc.form_type,
                accession_or_subtype=raw_doc.accession_number,
                filename=raw_doc.filename,
            )

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(raw_doc.content)

            log_info(f"📄 Saved {self.file_type.upper()} file: {path}")
            return path

        except Exception as e:
            log_error(f"❌ Failed to write {self.file_type.upper()} file for {raw_doc.accession_number}: {e}")
            raise

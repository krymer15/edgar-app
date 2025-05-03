import os
from pathlib import Path
from utils.path_manager import build_raw_filepath
from utils.get_project_root import get_project_root
from utils.report_logger import log_debug

class SgmlDocWriter:
    def __init__(self, base_data_path: str):
        self.base_data_path = base_data_path

    def save_raw_sgml(self, sgml_contents, year, cik, form_type, accession_clean, accession_full, filename):
        full_path = Path(build_raw_filepath(
            year=year,
            cik=cik,
            form_type=form_type,
            accession_or_subtype=accession_clean,
            filename=filename
        ))

        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(sgml_contents)

        log_debug(f"📁 [Writer] Saved raw SGML to: {full_path}")

        return full_path

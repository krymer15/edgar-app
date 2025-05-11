# orchestrators/base/xml_orchestrator_base.py

from abc import ABC, abstractmethod
from utils.path_manager import build_raw_filepath
from utils.url_builder import construct_primary_document_url
from writers.forms.xml_metadata_writer import log_xml_metadata
from datetime import datetime
import os

class XmlOrchestratorBase(ABC):
    def __init__(self, db_session, logger=None):
        self.db_session = db_session
        self.logger = logger or print

    @abstractmethod
    def parse_content(self, xml_str: str, meta: dict) -> dict:
        """Form-specific parser override (e.g., Form 4 vs 13D)"""
        pass

    @abstractmethod
    def write_to_db(self, parsed: dict):
        """Form-specific DB writer override"""
        pass

    def run(self, meta: dict, filename: str):
        accession_number = meta["accession_number"]
        cik = meta["cik"]
        filing_date = meta["filing_date"]
        form_type = meta["form_type"]
        year = str(datetime.strptime(filing_date, "%Y-%m-%d").year)

        url = construct_primary_document_url(cik, accession_number, filename)
        xml_path = build_raw_filepath(
            year=year,
            cik=cik,
            form_type=form_type,
            accession_or_subtype=accession_number.replace("-", ""),
            filename=filename
        )

        try:
            from downloaders.form4_xml_downloader import Form4XmlDownloader
            downloader = Form4XmlDownloader(cik, accession_number, form_type, filing_date)
            downloader.downloader.download_to_file(url, xml_path)
        except Exception as e:
            self.logger(f"[ERROR] Download failed: {e}")
            self.log_xml_meta(meta, filename, downloaded=False, parsed=False)
            return

        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                xml_content = f.read()
        except Exception as e:
            self.logger(f"[ERROR] Read failed: {e}")
            self.log_xml_meta(meta, filename, downloaded=True, parsed=False)
            return

        parsed = self.parse_content(xml_content, meta)
        if "error" in parsed:
            self.logger(f"[ERROR] Parse error: {parsed['error']}")
            self.log_xml_meta(meta, filename, downloaded=True, parsed=False)
            return

        self.write_to_db(parsed)
        self.log_xml_meta(meta, filename, downloaded=True, parsed=True)
        self.logger(f"[INFO] Parsed + saved {form_type}: {accession_number}")

    def log_xml_meta(self, meta: dict, filename: str, downloaded: bool, parsed: bool):
        log_xml_metadata({
            "accession_number": meta["accession_number"],
            "filename": filename,
            "downloaded": downloaded,
            "parsed_successfully": parsed
        })

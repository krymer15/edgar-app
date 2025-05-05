# downloaders/form4_xml_downloader.py

import os

from downloaders.sec_downloader import SecDownloader
from utils.path_manager import build_raw_filepath
from writers.xml_metadata_writer import log_xml_metadata
from utils.url_builder import construct_primary_document_url
from datetime import datetime


class Form4XmlDownloader:
    def __init__(self, cik: str, accession: str, form_type: str, filing_date: str):
        self.cik = cik
        self.accession = accession
        self.form_type = form_type.lower().replace(" ", "")
        self.filing_date = filing_date  # yyyy-mm-dd

        self.year = str(datetime.strptime(filing_date, "%Y-%m-%d").year)
        self.downloader = SecDownloader()

    def download_selected_files(self, file_list: list[str]) -> list[str]:
        """
        Download only selected XML files for a Form 4 accession.
        Args:
            file_list (list[str]): Specific XML filenames to download (e.g., ["xslF345X05_primary.xml"])
        Returns:
            List of full file paths that were saved locally
        """
        saved_files = []

        for filename in file_list:
            url = construct_primary_document_url(cik=self.cik, accession_number=self.accession, filename=filename)
            raw_path = build_raw_filepath(
                year=self.year,
                cik=self.cik,
                form_type=self.form_type,
                accession_or_subtype=self.accession,
                filename=filename
            )
            
            # Download and write
            try:
                self.downloader.download_to_file(url, raw_path)
                saved_files.append(raw_path)
                downloaded = True
            except Exception as e:
                print(f"[ERROR] Failed to download {filename}: {e}")
                downloaded = False

            # ✅ Log XML metadata (regardless of success)
            log_xml_metadata({
                "accession_number": self.accession,
                "filename": filename,
                "downloaded": downloaded,
                "parsed_successfully": False
            })

        return saved_files

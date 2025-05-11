# Coordinates parsing/writing for Form 4 XML
# Needs cleanup and maybe refactoring!

import os
from orchestrators.base_orchestrator import BaseOrchestrator
from parsers.filing_parser_manager import FilingParserManager
from writers.forms.form4_writer import Form4Writer
from writers.forms.xml_metadata_writer import log_xml_metadata
from downloaders.form4_xml_downloader import Form4XmlDownloader
from utils.path_manager import build_raw_filepath
from utils.url_builder import construct_primary_document_url
from datetime import datetime

class Form4XmlOrchestrator(BaseOrchestrator):
    def __init__(self, db_session, logger=None):
        super().__init__(db_session, logger)
        self.parser_router = FilingParserManager()
        self.writer = Form4Writer(db_session)

    def parse_content(self, xml_str: str, meta: dict) -> dict:
        return self.parser_router.route(
            form_type=meta["form_type"],
            content=xml_str,
            metadata=meta
        )

    def write_to_db(self, parsed: dict):
        self.writer.write_content(parsed)

    def run(self, meta: dict, filename: str):
        """
        Downloads a specific Form 4 XML, parses it, and writes result to DB.

        Args:
            meta (dict): Must include 'cik', 'accession_number', 'filing_date', 'form_type'
            filename (str): Exact filename to download and parse (e.g., "xslF345X05_primary.xml")
        """
        cik = meta["cik"]
        accession_number = meta["accession_number"]
        form_type = meta.get("form_type", "4")
        filing_date = meta["filing_date"]
        year = str(datetime.strptime(filing_date, "%Y-%m-%d").year)

        # Step 1: Build URL + local path
        url = construct_primary_document_url(cik, accession_number, filename)
        xml_path = build_raw_filepath(
            year=year,
            cik=cik,
            form_type=form_type,
            accession_or_subtype=accession_number.replace("-", ""),
            filename=filename
        )

        # Step 2: Download
        try:
            downloader = Form4XmlDownloader(cik, accession_number, form_type, filing_date)
            downloader.downloader.download_to_file(url, xml_path)
        except Exception as e:
            self.logger(f"[ERROR] Failed to download XML: {e}")
            return

        # Step 3: Parse
        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                xml_content = f.read()
        except Exception as e:
            self.logger(f"[ERROR] Could not read XML file: {e}")
            return

        parsed = self.parser_router.route(
            form_type=form_type,
            content=xml_content,
            metadata={
                "accession_number": accession_number,
                "filing_date": filing_date,
                "cik": cik
            }
        )

        if "error" in parsed:
            self.logger(f"[ERROR] Parsing failed: {parsed['error']}")
            return

        # Step 4: Write to DB
        parsed.update({
            "accession_number": accession_number,
            "filing_date": filing_date,
            "cik": cik,
            "form_type": form_type,
        })
        self.writer.write_content(parsed)

        # ✅ Update XML metadata to mark parsed_successfully = True
        log_xml_metadata({
            "accession_number": accession_number,
            "filename": filename,
            "downloaded": True,  # assumed if we parsed it
            "parsed_successfully": True
        })
        self.logger(f"[INFO] Parsed + saved Form 4: {accession_number}")
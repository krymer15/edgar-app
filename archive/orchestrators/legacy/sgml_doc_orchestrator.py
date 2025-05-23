import requests
import time
from config.config_loader import ConfigLoader
from utils.url_builder import construct_sgml_txt_url
from parsers.sgml_filing_parser import SgmlFilingParser
from archive.writers.sgml_doc_writer import SgmlDocWriter
from archive.writers.parsed_sgml_writer import ParsedSgmlWriter
from utils.path_utils import build_path_args
from utils.path_manager import build_raw_filepath
from utils.report_logger import log_info, log_debug, log_error, log_warn

class SgmlDocOrchestrator:
    # write_to_db = true if running this orch isolated (outside the batch orch). Otherwise BatchSgmlIngestionOrchestrator tries to write 2x to `parsed_sgml_metadata`
    def __init__(self, save_raw: bool = True, write_to_db: bool = False):
        self.config = ConfigLoader.load_config()
        self.base_data_path = self.config.get("storage", {}).get("base_data_path", "./data/")
        log_debug(f"base_data_path resolved to: {self.base_data_path}")
        self.user_agent = self.config.get("sec_downloader", {}).get("user_agent")
        self.save_raw = save_raw
        self.write_to_db = write_to_db

    def run(self, cik: str, accession_full: str, form_type: str, filing_date: str):
        year = filing_date[:4]

        # ⚠️ accession_clean is for local use only — do not persist or pass downstream.
        accession_clean = accession_full.replace("-", "")
        sgml_filename = f"{accession_full}.txt"

        sgml_url = construct_sgml_txt_url(cik, accession_clean)
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }

        log_info(f"📥 Downloading SGML: {sgml_url}")
        response = requests.get(sgml_url, headers=headers)

        if response.status_code != 200:
            log_warn(f"⚠️ First attempt failed with status {response.status_code}. Retrying...")
            time.sleep(1)
            response = requests.get(sgml_url, headers=headers)

        if response.status_code != 200:
            log_error(f"[ERROR] Download failed after retry: {sgml_url} (status {response.status_code})")
            return

        sgml_contents = response.text

        if self.save_raw:
            log_debug("Preparing to write SGML to disk...")
            writer = SgmlDocWriter(base_data_path=self.base_data_path)
            writer.save_raw_sgml(
                sgml_contents=sgml_contents,
                year=year,
                cik=cik,
                form_type=form_type,
                accession_clean=accession_clean,
                accession_full=accession_full,
                filename=sgml_filename
            )
            log_debug("SGML file write complete.")

        parser = SgmlFilingParser(cik=cik, accession_number=accession_clean, form_type=form_type)
        result = parser.parse(sgml_contents)

        # for ex in result["exhibits"]:
        #     tag = "✅" if ex.get("accessible", True) else "❌"
        #     log_info(f"{tag} {ex['filename']} | {ex['description']} | {ex['type']}")

        log_info(f"🔗 Likely Primary Document URL:\n{result['primary_document_url']}")
        
        # Write to database; We use accession_full (with dashes) to match the DB key field and avoid conflicts with the accession_clean rule.
        # Metadata and exhibits will be written by batch orchestrator after validation. Below code can be activated with a bool switch for isolated (outside batch orch) runs like this:
        if self.write_to_db:
            writer = ParsedSgmlWriter()
            try:
                writer.write_metadata({
                    "accession_number": accession_full,
                    "form_type": form_type,
                    "primary_doc_url": result["primary_document_url"]
                })
                writer.write_exhibits(
                    result["exhibits"],
                    accession_number=accession_full,
                    cik=cik,
                    form_type=form_type,
                    filing_date=filing_date,
                    primary_doc_url=result.get("primary_document_url", "")
                )

            finally:
                writer.close()

        return result

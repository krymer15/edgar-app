# orchestrators/filing_documents_orchestrator.py

# Parses SGML .txt to populate filing_documents

from models.parsed_document import ParsedDocument
from models.filing_metadata import FilingMetadata
from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter
from parsers.sgml_document_processor import SgmlDocumentProcessor
from utils.path_utils import build_path_args
from models.database import SessionLocal
from config.config_loader import ConfigLoader
from utils.report_logger import log_info, log_error, log_warn
from utils.url_builder import construct_sgml_txt_url

class FilingDocumentsOrchestrator:
    def __init__(self, limit: int = 100):
        self.session = SessionLocal()
        self.writer = FilingDocumentsWriter()
        self.limit = limit
        config = ConfigLoader.load_config()
        self.processor = SgmlDocumentProcessor(
            user_agent=config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")
        )

    def orchestrate(self, limit: int):
        filings = self.session.query(FilingMetadata).limit(limit).all()
        for record in filings:
            try:
                self.process_record(record)
            except Exception as e:
                log_error(f"Failed to process {record.accession_number}: {e}")
        self.session.close()

    def process_record(self, record: FilingMetadata):
        log_info(f"🔍 Processing {record.accession_number}")

        sgml_url = construct_sgml_txt_url(record.cik, record.accession_number) # Construct SGML .txt. URL

        parsed_documents = self.processor.process(
            cik=record.cik,
            accession_number=record.accession_number,
            form_type=record.form_type,
            sgml_url=sgml_url
        )

        log_info(f"📄 Parsed {len(parsed_documents)} documents for {record.accession_number}")
        if not parsed_documents:
            log_warn(f"No documents parsed from {record.accession_number}")
        self.writer.write_documents(parsed_documents)

    def run(self, date_str: str, limit: int):
        print(f"Running FilingDocumentsOrchestrator for {date_str}")  # 👈 for CLI test capture
        log_info(f"Running FilingDocumentsOrchestrator for {date_str}")
        self.orchestrate(limit=limit)
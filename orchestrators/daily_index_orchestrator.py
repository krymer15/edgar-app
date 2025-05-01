# orchestrators/daily_index_orchestrator.py

from orchestrators.base_orchestrator import BaseOrchestrator
from utils.path_utils import build_path_args
import utils.path_manager as path_manager
from orchestrators.embedded_doc_orchestrator import EmbeddedDocOrchestrator

class DailyIndexOrchestrator(BaseOrchestrator):
    """
    ⚠️ NOTE:
    Daily Index (.idx) ingestion pipeline only provides limited metadata per filing:
    - Company Name, Form Type, CIK, Date Filed, URL.

    Unlike Submissions API, no accession numbers or primary document names are available.
    This limits precise filepath construction unless supplemental fetching (e.g., index.json lookup) is added later.
    """

    def __init__(self, collector, parser, writer, fetcher, downloader, content_parser, content_writer):
        self.collector = collector
        self.parser = parser
        self.writer = writer
        self.fetcher = fetcher
        self.downloader = downloader
        self.content_parser = content_parser
        self.content_writer = content_writer

    def orchestrate(self, date: str = None, limit: int = 5):
        """
        Implement base orchestrate method by chaining metadata and content ingestion.
        """
        if not date:
            raise ValueError("Date must be provided for daily index ingestion.")
        
        # Step 1: Collect and save to Postgres
        self.orchestrate_metadata_ingestion(date)

        # Step 2: Download + process filings
        self.orchestrate_content_ingestion(since_date=date, limit=limit)

    def orchestrate_metadata_ingestion(self, date: str):
        """Collect and save Daily Index metadata."""
        raw_metadata = self.collector.collect(date)
        print(f"✅ Parsed {len(raw_metadata)} filings from crawler.idx")
        self.writer.write_metadata(raw_metadata)
        print(f"✅ Saved {len(raw_metadata)} filings into daily_index_metadata")

    def orchestrate_content_ingestion(self, since_date=None, limit: int | None = None):
        """Download, parse, and save filings based on stored metadata."""
        filings_metadata = self.fetcher.get_urls_for_download(since_date)
        if limit:
            filings_metadata = filings_metadata[:limit]

        for filing in filings_metadata:
            url = filing["url"]
            cik = filing.get("cik")
            form_type = filing.get("form_type")
            filing_date = filing.get("filing_date")

            # Step 1: Download index.html
            raw_html = self.downloader.download(url)

            # Step 2: Parse for accession + embedded doc URL
            parsed_data = self.content_parser.parse(raw_html, url, cik, form_type, filing_date)
            accession = parsed_data.get("accession_number")
            embedded_url = parsed_data.get("primary_document_url")

            # Step 3: Save raw index.html
            raw_path_args = build_path_args({
                "filing_date": filing_date,
                "cik": cik,
                "form_type": form_type,
                "accession_number": accession,
            }, filename="index.html")
            raw_filepath = path_manager.build_raw_filepath(*raw_path_args)
            self.content_writer.write_filing_from_filepath(raw_html, filepath=raw_filepath)
            print(f"📁 [Debug] Saved index.html to: {raw_filepath}")

            # Step 4: Trigger Stage 2
            print(f"🧭 Found embedded primary doc URL: {embedded_url}")
            if embedded_url:
                embedded_orchestrator = EmbeddedDocOrchestrator(base_path="./test_data")
                embedded_orchestrator.run(
                    accession=accession,
                    cik=cik,
                    form_type=form_type,
                    filing_date=filing_date,
                    embedded_url=embedded_url
                )

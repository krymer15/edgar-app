# orchestrators/daily_index_orchestrator.py
from orchestrators.base_orchestrator import BaseOrchestrator

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

    def orchestrate(self, date: str = None):
        """
        Implement base orchestrate method by chaining metadata and content ingestion.
        """
        if not date:
            raise ValueError("Date must be provided for daily index ingestion.")
        
        self.orchestrate_metadata_ingestion(date)
        self.orchestrate_content_ingestion(since_date=date)

    def orchestrate_metadata_ingestion(self, date: str):
        """Collect and save Daily Index metadata."""
        raw_metadata = self.collector.collect(date)
        print(f"✅ Parsed {len(raw_metadata)} filings from crawler.idx")
        # structured_metadata = self.parser.parse(raw_metadata) --- skipped this parser step and modularize properly later
        self.writer.write_metadata(raw_metadata)
        print(f"✅ Saved {len(raw_metadata)} filings into daily_index_metadata")

    def orchestrate_content_ingestion(self, since_date=None):
        """Download, parse, and save filings based on stored metadata."""
        filings_metadata = self.fetcher.get_urls_for_download(since_date)

        for filing in filings_metadata:
            url = filing["url"]
            cik = filing.get("cik")
            form_type = filing.get("form_type")
            filing_date = filing.get("filing_date")

            raw_filing = self.downloader.download(url)

            parsed_content = self.content_parser.parse(
                raw_html=raw_filing,
                url=url,
                cik=cik,
                form_type=form_type,
                filing_date=filing_date
            )

            self.content_writer.write_content(parsed_content)


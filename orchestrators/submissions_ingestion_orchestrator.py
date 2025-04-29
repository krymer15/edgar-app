# orchestrators/submissions_ingestion_orchestrator.py

from orchestrators.base_orchestrator import BaseOrchestrator

class SubmissionsIngestionOrchestrator(BaseOrchestrator):
    def __init__(self, collector, downloader, writer, forms_filter=None):
        """
        Args:
            collector: SubmissionsCollector instance
            downloader: SECDownloader instance
            writer: File system writer or DB writer
            forms_filter: Optional list of form types to restrict (e.g., ["8-K", "10-K"])
        """
        self.collector = collector
        self.downloader = downloader
        self.writer = writer
        self.forms_filter = forms_filter

    def orchestrate(self, cik: str, limit: int = 5):
        """Orchestrate the full ingestion flow for a given company CIK."""

        # Step 1: Collect recent filings metadata
        filings_metadata = self.collector.collect(cik, forms_filter=self.forms_filter)

        if limit:
            filings_metadata = filings_metadata[:limit]  # Only take first N filings

        for filing in filings_metadata:
            filing_url = filing["filing_url"]
            accession_number = filing["accessionNumber"]
            form_type = filing["form"]
            filing_date = filing["filingDate"]

            try:
                # Step 2: Download the raw HTML filing
                raw_html = self.downloader.download_html(filing_url)

                # Step 3: Write raw HTML filing to storage
                self.writer.write_filing(
                    cik=cik,
                    accession_number=accession_number,
                    form_type=form_type,
                    filing_date=filing_date,
                    raw_html=raw_html
                )

                print(f"✅ Successfully processed {accession_number} ({form_type})")

            except Exception as e:
                print(f"❌ Error processing {accession_number}: {str(e)}")

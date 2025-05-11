# tests/test_submissions_ingestion_orchestrator.py

import unittest
from unittest.mock import MagicMock
from orchestrators.submissions_api.submissions_ingestion_orchestrator import SubmissionsIngestionOrchestrator

class TestSubmissionsIngestionOrchestrator(unittest.TestCase):
    def setUp(self):
        self.collector = MagicMock()
        self.downloader = MagicMock()
        self.writer = MagicMock()

        self.orchestrator = SubmissionsIngestionOrchestrator(
            collector=self.collector,
            downloader=self.downloader,
            writer=self.writer,
            forms_filter=["8-K"]
        )

    def test_orchestrate_success_flow(self):
        self.collector.collect.return_value = [
            {
                "filing_url": "https://sec.gov/fake-filing",
                "accessionNumber": "0001234567-23-000001",
                "form": "8-K",
                "filingDate": "2023-01-01",
            }
        ]

        self.downloader.download_html.return_value = "<html>Test Filing</html>"

        self.orchestrator.orchestrate(cik="1234567890", limit=1)

        self.collector.collect.assert_called_once()
        self.downloader.download_html.assert_called_once()
        self.writer.write_filing.assert_called_once()

if __name__ == "__main__":
    unittest.main()

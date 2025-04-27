# tests/test_orchestrator.py

import unittest
import os

from utils.config_loader import ConfigLoader
from utils.ticker_cik_mapper import TickerCIKMapper
from downloaders.sec_downloader import SECDownloader
from utils.file_saver import save_html_to_file, save_text_blocks_to_file
from parsers.exhibit_parser import ExhibitParser
from utils.get_project_root import get_project_root

class TestOrchestratorSingleFiling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup shared objects once for all tests.
        """
        cls.config = ConfigLoader.load_config()
        cls.mapper = TickerCIKMapper()
        cls.test_ticker = "MRVL"  # Example ticker
        cls.test_cik = cls.mapper.get_cik(cls.test_ticker)

        cls.downloader = SECDownloader(
            cik=cls.test_cik,
            user_agent=cls.config["sec_downloader"]["user_agent"],
            request_delay_seconds=cls.config["sec_downloader"]["request_delay_seconds"]
        )

    def test_process_single_filing(self):
        """
        Test processing one filing end-to-end.
        """
        # Fetch metadata
        self.downloader.fetch_submissions()
        self.downloader.extract_recent_filings()
        filings = self.downloader.build_filing_urls(forms_filter=["8-K", "10-K"])

        self.assertTrue(len(filings) > 0, "No 8-K or 10-K filings found.")

        # Process first filing
        filing = filings[0]
        filing_url = filing["filing_url"]

        try:
            raw_html = self.downloader.download_html(filing_url)
        except Exception as e:
            self.fail(f"Failed to download filing HTML: {e}")

        # Parse exhibit
        parser = ExhibitParser(html_content=raw_html)
        parser.parse()
        cleaned_text = parser.get_cleaned_text()

        # Save outputs
        project_root = get_project_root()
        output_dir = os.path.join(project_root, "tests", "output")
        os.makedirs(output_dir, exist_ok=True)

        raw_html_path = os.path.join(output_dir, "test_filing_raw.html")
        text_blocks_path = os.path.join(output_dir, "test_filing_blocks.txt")

        save_html_to_file(raw_html, raw_html_path)
        save_text_blocks_to_file(cleaned_text.split("\n\n"), text_blocks_path)

        # Assertions to check file creation
        self.assertTrue(os.path.exists(raw_html_path), "Raw HTML file not created.")
        self.assertTrue(os.path.exists(text_blocks_path), "Parsed blocks file not created.")

if __name__ == "__main__":
    unittest.main()

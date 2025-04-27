# test_sec_downloader.py

import unittest
from unittest.mock import patch, MagicMock
from downloaders.sec_downloader import SECDownloader

class TestSECDownloader(unittest.TestCase):

    def setUp(self):
        """Set up the downloader instance for testing."""
        self.downloader = SECDownloader(cik="1234567", delay=0.1)  # Provide dummy CIK

    @patch("downloaders.sec_downloader.requests.get")
    def test_download_html_success(self, mock_get):
        """Test downloading HTML successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test Filing</body></html>"
        mock_get.return_value = mock_response

        url = "https://www.sec.gov/test-filing.html"
        html = self.downloader.download_html(url)

        self.assertIn("Test Filing", html)
        mock_get.assert_called_once()

    @patch("downloaders.sec_downloader.save_metadata_to_json")
    @patch("downloaders.sec_downloader.requests.get")
    def test_fetch_submissions_success(self, mock_get, mock_save_metadata):
        """Test fetching submissions JSON successfully and saving metadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "filings": {
                "recent": {
                    "accessionNumber": ["0001234567-23-000001"],
                    "primaryDocument": ["testdoc.htm"],
                    "filingDate": ["2023-01-01"],
                    "form": ["8-K"]
                }
            }
        }

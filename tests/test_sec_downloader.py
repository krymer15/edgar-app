# tests/test_sec_downloader.py

import unittest
from unittest.mock import patch, MagicMock
from downloaders.sec_downloader import SECDownloader

class TestSECDownloader(unittest.TestCase):
    def setUp(self):
        self.downloader = SECDownloader(user_agent="test-agent@example.com", request_delay_seconds=0)

    @patch("downloaders.sec_downloader.requests.get")
    def test_download_html_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Success</body></html>"
        mock_get.return_value = mock_response

        html = self.downloader.download_html("https://www.sec.gov/test")
        self.assertIn("Success", html)

    @patch("downloaders.sec_downloader.requests.get")
    def test_download_json_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "value"}
        mock_get.return_value = mock_response

        data = self.downloader.download_json("https://www.sec.gov/test.json")
        self.assertEqual(data["test"], "value")

    @patch("downloaders.sec_downloader.requests.get")
    def test_download_method_aliases_download_html(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Alias Success</body></html>"
        mock_get.return_value = mock_response

        html = self.downloader.download("https://www.sec.gov/testalias")
        self.assertIn("Alias Success", html)

if __name__ == "__main__":
    unittest.main()

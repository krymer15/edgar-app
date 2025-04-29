# tests/test_submissions_collector.py

import unittest
from unittest.mock import patch, MagicMock
from collectors.submissions_collector import SubmissionsCollector

class TestSubmissionsCollector(unittest.TestCase):
    def setUp(self):
        self.collector = SubmissionsCollector(user_agent="test-agent@example.com")

    @patch("collectors.submissions_collector.SECDownloader.download_json")
    def test_collect_all_filings(self, mock_download_json):
        mock_download_json.return_value = {
            "filings": {
                "recent": {
                    "accessionNumber": ["0001234567-23-000001"],
                    "primaryDocument": ["testdoc.htm"],
                    "filingDate": ["2023-01-01"],
                    "form": ["8-K"],
                    "items": ["Item 1"],
                    "isXBRL": [False],
                }
            }
        }

        filings = self.collector.collect(cik="1234567890")
        self.assertEqual(len(filings), 1)
        self.assertEqual(filings[0]["form"], "8-K")

    @patch("collectors.submissions_collector.SECDownloader.download_json")
    def test_collect_filtered_forms(self, mock_download_json):
        mock_download_json.return_value = {
            "filings": {
                "recent": {
                    "accessionNumber": ["0001234567-23-000001"],
                    "primaryDocument": ["testdoc.htm"],
                    "filingDate": ["2023-01-01"],
                    "form": ["S-8"],
                    "items": ["Item 1"],
                    "isXBRL": [False],
                }
            }
        }

        filings = self.collector.collect(cik="1234567890", forms_filter=["8-K", "10-Q"])
        self.assertEqual(len(filings), 0)  # S-8 is filtered out

if __name__ == "__main__":
    unittest.main()

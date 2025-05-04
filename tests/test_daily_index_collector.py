# tests/test_daily_index_collector.py

import unittest
from unittest.mock import patch
from collectors.daily_index_collector import DailyIndexCollector


class TestDailyIndexCollector(unittest.TestCase):
    @patch("collectors.daily_index_collector.requests.get")
    def test_collect_parses_valid_lines(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """\
CIK       Company Name       Form Type    Date Filed   Filename
---------------------------------------------------------------
000001    ACME Corp           8-K          20250401     edgar/data/000001/000001-index.htm
"""

        collector = DailyIndexCollector(user_agent="TestBot/1.0")
        result = collector.collect(date="2025-04-01")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cik"], "000001")
        self.assertEqual(result[0]["form_type"], "8-K")
        self.assertEqual(result[0]["accession_number"], "000001-25-000001")


if __name__ == "__main__":
    unittest.main()

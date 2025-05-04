# tests/test_daily_index_writer.py

import unittest
from unittest.mock import patch, MagicMock
from writers.daily_index_writer import DailyIndexWriter


class TestDailyIndexWriter(unittest.TestCase):
    @patch("writers.daily_index_writer.SessionLocal")
    def test_write_merges_and_commits(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        writer = DailyIndexWriter()
        writer.session = mock_session

        data = [{
            "cik": "000001",
            "form_type": "8-K",
            "filing_date": "2025-04-01",
            "filing_url": "edgar/data/000001/000001-index.htm",
            "accession_number": "000001"
        }]
        writer.write(data)
        self.assertTrue(mock_session.merge.called)
        self.assertTrue(mock_session.commit.called)


if __name__ == "__main__":
    unittest.main()

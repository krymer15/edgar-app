# tests/test_parsed_sgml_writer.py

import unittest
from unittest.mock import patch, MagicMock
from writers.parsed_sgml_writer import ParsedSgmlWriter


class TestParsedSgmlWriter(unittest.TestCase):
    def setUp(self):
        self.writer = ParsedSgmlWriter()

    @patch("writers.parsed_sgml_writer.SessionLocal")
    def test_write_metadata_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        self.writer.session = mock_session

        metadata = {
            "accession_number": "000001",
            "cik": "1234567",
            "form_type": "8-K",
            "filing_date": "2025-01-01",
            "primary_document_url": "https://sec.gov/test"
        }

        self.writer.write_metadata(metadata)
        self.assertTrue(mock_session.add.called)
        self.assertTrue(mock_session.commit.called)

    @patch("writers.parsed_sgml_writer.SessionLocal")
    def test_write_exhibits_filters_and_commits(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session_cls.return_value = mock_session
        self.writer.session = mock_session

        exhibits = [
            {"filename": "ex1.htm", "description": "D1", "type": "EX-99.1", "accessible": True},
            {"filename": "ex2.htm", "description": "D2", "type": "EX-99.2", "accessible": False}
        ]

        self.writer.write_exhibits(
            exhibits=exhibits,
            accession_number="000001",
            cik="1234567",
            form_type="8-K",
            filing_date="2025-01-01",
            primary_doc_url="https://sec.gov/test"
        )
        self.assertTrue(mock_session.commit.called)


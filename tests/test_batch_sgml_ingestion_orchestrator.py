# tests/test_batch_sgml_ingestion_orchestrator.py

# At the top of test_single_sgml_orchestrator.py, test_batch_sgml_ingestion_orchestrator.py, etc.
from utils.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

import unittest
from unittest.mock import patch, MagicMock
from orchestrators.batch_sgml_ingestion_orchestrator import BatchSgmlIngestionOrchestrator


class TestBatchSgmlIngestionOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_date = "2025-04-28"
        self.mock_filing_meta = [
            {
                "accession_number": "0001437749-25-013070",
                "cik": "1084869",
                "form_type": "8-K",
                "filing_date": "2025-04-25"
            }
        ]
        self.mock_result = {
            "primary_document_url": "https://example.com/doc.htm",
            "exhibits": [
                {"filename": "doc1.htm", "description": "Doc 1", "type": "EX-99.1", "accessible": True}
            ]
        }

    @patch("orchestrators.batch_sgml_ingestion_orchestrator.SgmlDocOrchestrator")
    @patch("orchestrators.batch_sgml_ingestion_orchestrator.DailyIndexCollector")
    def test_orchestrate_runs_without_crash(self, mock_collector_cls, mock_orchestrator_cls):
        mock_collector = MagicMock()
        mock_collector.collect.return_value = self.mock_filing_meta
        mock_collector_cls.return_value = mock_collector

        mock_orchestrator = MagicMock()
        mock_orchestrator.run.return_value = self.mock_result
        mock_orchestrator_cls.return_value = mock_orchestrator

        orchestrator = BatchSgmlIngestionOrchestrator(date_str=self.test_date, limit=1)
        try:
            orchestrator.orchestrate()
        except Exception as e:
            self.fail(f"orchestrate() raised an exception unexpectedly: {e}")

        mock_collector.collect.assert_called_once()
        mock_orchestrator.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()

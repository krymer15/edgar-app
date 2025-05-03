# tests/test_batch_sgml_ingestion_orchestrator.py

import unittest
from orchestrators.batch_sgml_ingestion_orchestrator import BatchSgmlIngestionOrchestrator

class TestBatchSgmlIngestionOrchestrator(unittest.TestCase):
    def setUp(self):
        # Use a date with a known small number of filings for test purposes
        self.test_date = "2025-04-28"
        self.orchestrator = BatchSgmlIngestionOrchestrator(target_date=self.test_date, limit=2)

    def test_instantiation(self):
        self.assertEqual(self.orchestrator.target_date, self.test_date)
        self.assertEqual(self.orchestrator.limit, 2)
        self.assertIsNotNone(self.orchestrator.collector)
        self.assertIsNotNone(self.orchestrator.doc_orchestrator)

    def test_orchestrate_runs_without_crash(self):
        try:
            self.orchestrator.orchestrate()
        except Exception as e:
            self.fail(f"orchestrate() raised an exception unexpectedly: {e}")

if __name__ == "__main__":
    unittest.main()

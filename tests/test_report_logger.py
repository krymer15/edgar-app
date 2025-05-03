import unittest
import tempfile
import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.report_logger import append_ingestion_report

class TestReportLogger(unittest.TestCase):
    def test_append_ingestion_report_creates_file_and_row(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "ingestion_test_log.csv"

            row = {
                "accession_number": "0001234567-25-000001",
                "cik": "0001234567",
                "form_type": "8-K",
                "filing_date": "2025-05-03",
                "exhibits_written": 1,
                "exhibits_skipped": 0,
                "primary_doc_url": "https://www.sec.gov/Archives/example"
            }

            append_ingestion_report(row, output_path=temp_path)

            self.assertTrue(temp_path.exists())

            with open(temp_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self.assertEqual(len(rows), 1)
            self.assertIn("timestamp", rows[0])
            self.assertEqual(rows[0]["accession_number"], row["accession_number"])

if __name__ == "__main__":
    unittest.main()

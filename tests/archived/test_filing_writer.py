# tests/test_filing_writer.py

import unittest
import os
import shutil
from archive.writers.filing_writer import FilingWriter

class TestFilingWriter(unittest.TestCase):
    def setUp(self):
        self.test_base_dir = "tests/test_data/"
        self.writer = FilingWriter(base_dir=self.test_base_dir)

    def tearDown(self):
        shutil.rmtree(self.test_base_dir, ignore_errors=True)

    def test_write_filing_creates_file(self):
        cik = "1234567890"
        accession_number = "0001234567-23-000001"
        form_type = "8-K"
        filing_date = "2023-01-01"
        raw_html = "<html><body>Test Filing</body></html>"

        self.writer.write_filing(cik, accession_number, form_type, filing_date, raw_html)

        expected_path = os.path.join(
            self.test_base_dir,
            cik,
            f"{filing_date}_{form_type}_{accession_number.replace('-', '')}.html"
        )
        self.assertTrue(os.path.exists(expected_path))

    def test_write_content_creates_file(self):
        parsed_content = {
            "filepath": "test_folder/test_filing.html",
            "content": "<html>Test Content</html>"
        }

        self.writer.write_content(parsed_content)

        expected_path = os.path.join(self.test_base_dir, "test_folder", "test_filing.html")
        self.assertTrue(os.path.exists(expected_path))

if __name__ == "__main__":
    unittest.main()

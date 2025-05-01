import unittest
import os
from pathlib import Path
from writers.sgml_doc_writer import SgmlDocWriter

class TestSgmlDocWriter(unittest.TestCase):
    def setUp(self):
        self.writer = SgmlDocWriter(base_data_path="./test_data/")
        self.sgml_contents = "Sample SGML text"
        self.year = "2025"
        self.cik = "1084869"
        self.form_type = "8-K"
        self.accession = "000143774925013070"
        self.filename = "sample_sgml.txt"

    def test_save_raw_sgml_creates_file(self):
        filepath = self.writer.save_raw_sgml(
            sgml_contents=self.sgml_contents,
            year=self.year,
            cik=self.cik,
            form_type=self.form_type,
            accession_clean=self.accession,
            accession_full="0001437749-25-013070",
            filename=self.filename
        )
        self.assertTrue(Path(filepath).exists())
        with open(filepath, "r") as f:
            content = f.read()
        self.assertEqual(content, self.sgml_contents)

    def tearDown(self):
        # Cleanup created file and parent dirs
        raw_dir = Path(self.writer.base_data_path) / self.year / self.cik / self.form_type / self.accession
        if raw_dir.exists():
            for file in raw_dir.glob("*"):
                file.unlink()
            raw_dir.rmdir()
            raw_dir.parent.rmdir()
            raw_dir.parent.parent.rmdir()

if __name__ == "__main__":
    unittest.main()

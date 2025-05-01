import os
import unittest
from utils.path_manager import build_raw_filepath, build_processed_filepath

class TestPathManager(unittest.TestCase):
    def test_build_raw_filepath(self):
        result = build_raw_filepath(
            year="2025",
            cik="1084869",
            form_type="8-K",
            accession_or_subtype="000143774925013070",
            filename="example.txt"
        )
        self.assertIn("2025", result)
        self.assertTrue(result.endswith("example.txt"))

    def test_build_processed_filepath(self):
        result = build_processed_filepath(
            year="2025",
            cik="1084869",
            form_type="8-K",
            accession_or_subtype="000143774925013070",
            filename="parsed.json"
        )
        self.assertIn("2025", result)
        self.assertTrue(result.endswith("parsed.json"))

if __name__ == "__main__":
    unittest.main()

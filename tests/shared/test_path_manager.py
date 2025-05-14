
import sys, os

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import unittest
from utils.path_manager import build_raw_filepath, build_processed_filepath, build_cache_path, build_raw_filepath_by_type

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

    def test_build_raw_filepath_by_type(self):
        result = build_raw_filepath_by_type(
            file_type="sgml",
            year="2024",
            cik="0000320193",
            form_type="10-K",
            accession_or_subtype="000032019324000011",
            filename="submission.txt"
        )
        # Verify structure
        self.assertTrue(result.replace("\\", "/").endswith(
            "0000320193/2024/10-K/000032019324000011/submission.txt"
        ))

        result_html = build_raw_filepath_by_type(
            file_type="html_index",
            year="2024",
            cik="0000320193",
            form_type="10-K",
            accession_or_subtype="000032019324000011",
            filename="index.html"
        )
        self.assertTrue(result_html.replace("\\", "/").endswith(
            "0000320193/2024/10-K/000032019324000011/index.html"
        ))
        self.assertTrue(result_html.endswith("index.html"))

        # Test invalid type
        with self.assertRaises(ValueError):
            build_raw_filepath_by_type(
                file_type="pdf",  # unsupported
                year="2024",
                cik="0000320193",
                form_type="10-K",
                accession_or_subtype="000032019324000011",
                filename="doc.pdf"
            )

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

    def test_build_cache_path(self):
        path = build_cache_path("0123456789", "20250412000001", year="2025")
        self.assertIn("cache_sgml", path)
        self.assertIn("0123456789", path)
        self.assertTrue(path.endswith("20250412000001.txt"))

if __name__ == "__main__":
    unittest.main()

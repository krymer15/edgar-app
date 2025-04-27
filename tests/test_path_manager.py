import os
import unittest
from utils.path_manager import build_raw_filepath, build_processed_filepath

class TestPathManager(unittest.TestCase):
    def test_build_raw_filepath(self):
        subpath = "mrvl/2025-04-26/mrvl-8k-20250426.htm"
        expected = os.path.normpath("data/raw/mrvl/2025-04-26/mrvl-8k-20250426.htm")
        result = build_raw_filepath(subpath)
        self.assertEqual(result, expected)

    def test_build_processed_filepath(self):
        subpath = "mrvl/2025-04-26/parsed_blocks.txt"
        expected = os.path.normpath("data/processed/mrvl/2025-04-26/parsed_blocks.txt")
        result = build_processed_filepath(subpath)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()

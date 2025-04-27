import os
import json
import unittest
from utils.file_saver import save_html_to_file, save_text_blocks_to_file, save_metadata_to_json

TEST_DIR = "tests/tmp/"

class TestFileSaver(unittest.TestCase):
    def setUp(self):
        """Create a temp directory for test outputs."""
        os.makedirs(TEST_DIR, exist_ok=True)

    def tearDown(self):
        """Clean up all files after each test."""
        for filename in os.listdir(TEST_DIR):
            filepath = os.path.join(TEST_DIR, filename)
            os.remove(filepath)

    def test_save_html_to_file(self):
        content = "<html><body><h1>Test Filing</h1></body></html>"
        filepath = os.path.join(TEST_DIR, "test_filing.html")
        save_html_to_file(content, filepath)

        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            read_content = f.read()
        self.assertEqual(read_content, content)

    def test_save_text_blocks_to_file(self):
        blocks = ["First block of text.", "Second block of text."]
        filepath = os.path.join(TEST_DIR, "test_blocks.txt")
        save_text_blocks_to_file(blocks, filepath)

        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            read_content = f.read()

        expected_content = "First block of text.\n\nSecond block of text.\n\n"
        self.assertEqual(read_content, expected_content)

    def test_save_metadata_to_json(self):
        metadata = {"company": "Test Corp", "filing_date": "2024-05-05", "form": "8-K"}
        filepath = os.path.join(TEST_DIR, "test_metadata.json")
        save_metadata_to_json(metadata, filepath)

        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            read_content = json.load(f)

        self.assertEqual(read_content, metadata)

if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path

import unittest
from utils.filtered_cik_manager import FilteredCikManager

class TestFilteredCikManager(unittest.TestCase):

    def setUp(self):
        # Create a temporary allowlist JSON file
        self.mock_cik_list = ["0001234567", "0009876543"]
        self.mock_file = "tests/mock_allowed_ciks.json"
        with open(self.mock_file, "w") as f:
            json.dump(self.mock_cik_list, f)
        self.allowed_forms = ["8-K", "10-K", "S-1"]

    def tearDown(self):
        import os
        if os.path.exists(self.mock_file):
            os.remove(self.mock_file)

    def test_filter_includes_only_valid_records(self):
        manager = FilteredCikManager(
            cik_allowlist_path=self.mock_file,
            allowed_form_types=self.allowed_forms
        )
        records = [
            {"cik": "0001234567", "form_type": "8-K"},
            {"cik": "0001111111", "form_type": "10-K"},
            {"cik": "0001234567", "form_type": "6-K"},
            {"cik": "0009876543", "form_type": "S-1"},
        ]
        filtered = manager.filter(records)
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r["cik"] in self.mock_cik_list for r in filtered))
        self.assertTrue(all(r["form_type"] in self.allowed_forms for r in filtered))

if __name__ == "__main__":
    unittest.main()

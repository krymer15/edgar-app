# test_exhibit_parser.py

import unittest
from parsers.exhibit_parser import ExhibitParser

class TestExhibitParser(unittest.TestCase):
    
    def setUp(self):
        """
        Prepare a simple mock HTML sample for testing.
        """
        self.sample_html = """
        <html>
            <body>
                <h1>Quarterly Earnings</h1>
                <table><tr><td>Revenue</td></tr></table>
                <p>This is the first paragraph.</p>
                <b>Important Update</b>
                <p>Additional details here.</p>
            </body>
        </html>
        """

    def test_parse_without_headers(self):
        """
        Test parsing without adding [HEADER] labels.
        """
        parser = ExhibitParser(self.sample_html, add_header_labels=False)
        parser.parse()
        output = parser.get_cleaned_text()
        
        self.assertNotIn("[HEADER]", output)
        self.assertIn("Quarterly Earnings", output)
        self.assertNotIn("Revenue", output)  # Table should be removed
        self.assertIn("This is the first paragraph.", output)

    def test_parse_with_headers(self):
        """
        Test parsing with [HEADER] labels added.
        """
        parser = ExhibitParser(self.sample_html, add_header_labels=True)
        parser.parse()
        output = parser.get_cleaned_text()

        self.assertIn("[HEADER] Important Update", output)
        self.assertIn("This is the first paragraph.", output)
        self.assertNotIn("Revenue", output)  # Ensure table removal still happens

if __name__ == "__main__":
    unittest.main()

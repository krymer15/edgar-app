import os
from dotenv import load_dotenv
import unittest
import requests
from parsers.sgml_filing_parser import SgmlFilingParser

class TestSgmlDocIntegration(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        company = os.getenv("EDGAR_COMPANY_NAME")
        email = os.getenv("EDGAR_EMAIL")
        user_agent = f"{company} ({email})"
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        self.cik = "1835632"
        self.accession = "0001835632-25-000051"
        self.form_type = "8-K"
        self.filing_date = "2025-03-05"
        self.txt_url = f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{self.accession.replace('-', '')}/{self.accession}.txt"

    def test_download_and_parse_sgml_filing(self):
        response = requests.get(self.txt_url, headers=self.headers)
        self.assertEqual(response.status_code, 200, f"Failed to download: {self.txt_url}")

        parser = SgmlFilingParser(self.cik, self.accession, self.form_type)
        result = parser.parse(response.text)

        self.assertGreater(len(result['exhibits']), 0, "No exhibits parsed")
        self.assertIsNotNone(result['primary_document_url'], "Primary document URL was not inferred")
        print("\nPrimary Document URL:", result['primary_document_url'])

if __name__ == '__main__':
    unittest.main()

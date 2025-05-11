# edgar-app/tests/test_ticker_cik_mapper.py

import unittest
from utils.ticker_cik_mapper import TickerCIKMapper

class TestTickerCIKMapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mapper = TickerCIKMapper(mapping_file="data/raw/company_tickers.json")

    def test_valid_ticker_uppercase(self):
        cik = self.mapper.get_cik("AAPL")
        self.assertEqual(len(cik), 10)
        self.assertTrue(cik.isdigit())

    def test_valid_ticker_lowercase(self):
        cik = self.mapper.get_cik("aapl")
        self.assertEqual(len(cik), 10)
        self.assertTrue(cik.isdigit())

    def test_valid_ticker_with_hyphen(self):
        cik = self.mapper.get_cik("BRK-B")
        self.assertEqual(len(cik), 10)
        self.assertTrue(cik.isdigit())

    def test_invalid_ticker_raises(self):
        with self.assertRaises(ValueError):
            self.mapper.get_cik("INVALIDTICKER")

    def test_empty_ticker_raises(self):
        with self.assertRaises(ValueError):
            self.mapper.get_cik("")

    def test_whitespace_ticker(self):
        cik = self.mapper.get_cik("  AAPL  ")
        self.assertEqual(len(cik), 10)
        self.assertTrue(cik.isdigit())

if __name__ == "__main__":
    unittest.main()

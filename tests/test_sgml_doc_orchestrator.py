# test_sgml_doc_orchestrator.py

# At the top of test_single_sgml_orchestrator.py, test_batch_sgml_ingestion_orchestrator.py, etc.
from utils.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

import unittest
from parsers.sgml_filing_parser import SgmlFilingParser

class TestSgmlFilingParser(unittest.TestCase):

    def setUp(self):
        self.sample_txt = """
<HEADER>
<ACCESSION-NUMBER>0001437749-25-013070
<CIK>1084869
<FORM-TYPE>8-K
<FILING-DATE>20250425
</HEADER>

<SEQUENCE>1
<FILENAME>flws20250425_8k.htm
<DESCRIPTION>FORM 8-K
<TYPE>8-K

<SEQUENCE>2
<FILENAME>exhibit99-1.htm
<DESCRIPTION>Press Release
<TYPE>EX-99.1

<SEQUENCE>3
<FILENAME>exhibit99-2.htm
<DESCRIPTION>Investor Deck
<TYPE>EX-99.2
"""
        self.parser = SgmlFilingParser(cik="1084869", accession_number="0001437749-25-013070", form_type="8-K")

    def test_sgml_exhibit_parsing(self):
        result = self.parser.parse(self.sample_txt)
        self.assertEqual(len(result['exhibits']), 3)
        self.assertEqual(result['exhibits'][0]['filename'], "flws20250425_8k.htm")

    def test_sgml_primary_doc_guess(self):
        result = self.parser.parse(self.sample_txt)
        self.assertEqual(result['primary_document_url'], "https://www.sec.gov/Archives/edgar/data/1084869/000143774925013070/flws20250425_8k.htm")

if __name__ == '__main__':
    unittest.main()

# parsers/sgml_document_processor.py

''' 
End-to-end service wrapper that fetches .txt, invokes the parser, and returns List[ParsedDocument]. 
- The orchestrated layer sitting atop SgmlFilingParser.
- Wrapper that fetches + parses.

This module will:
- Fetch the .txt SGML file from filing_metadata.filing_url
- Call SgmlFilingParser.parse_to_documents()
- Return List[ParsedDocument] or raise/log on failure
'''

# parsers/sgml_document_processor.py

import requests
from typing import List
from models.parsed_document import ParsedDocument
from parsers.sgml_filing_parser import SgmlFilingParser
from utils.report_logger import log_info, log_warn, log_error

class SgmlDocumentProcessor:
    def __init__(self, user_agent: str):
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }

    def process(self, cik: str, accession_number: str, form_type: str, sgml_url: str) -> List[ParsedDocument]:
        log_info(f"📥 Downloading SGML .txt for {accession_number}")
        response = requests.get(sgml_url, headers=self.headers)

        if response.status_code != 200:
            log_warn(f"⚠️ First attempt failed ({response.status_code}) — retrying...")
            response = requests.get(sgml_url, headers=self.headers)

        if response.status_code != 200:
            log_error(f"❌ Failed to fetch SGML file after retry: {sgml_url}")
            raise Exception(f"Failed to download SGML: {sgml_url}")

        parser = SgmlFilingParser(
            cik=cik,
            accession_number=accession_number,
            form_type=form_type
        )

        return parser.parse_to_documents(response.text)

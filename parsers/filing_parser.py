# parsers/filing_parser.py

from parsers.base_parser import BaseParser
import re

class FilingParser(BaseParser):
    def parse(self, raw_html: str, url: str = None, cik: str = None, form_type: str = None, filing_date: str = None) -> dict:
        """
        Parse the raw HTML of a filing index page to extract meaningful content.

        Args:
            raw_html (str): Raw HTML content of the filing index page.
            url (str): URL where the index page was fetched from.
            cik (str): Company CIK.
            form_type (str): Form type (e.g., 8-K, 10-Q).
            filing_date (str): Filing date in YYYY-MM-DD format.

        Returns:
            dict: Dictionary with 'filepath' and 'content' keys.
        """

        accession_number = None
        if url:
            match = re.search(r'/data/\d+/(\d{10}-\d{2}-\d{6})-index\.htm', url)
            if match:
                accession_number = match.group(1).replace("-", "")
        
        if not accession_number:
            accession_number = "unknown"

        if not cik:
            cik = "unknown_cik"
        if not form_type:
            form_type = "unknown_form"
        if not filing_date:
            filing_date = "unknown_date"

        # Build the filepath (primary document still unknown — use placeholder)
        filepath = f"{cik}/{filing_date}_{form_type}_{accession_number}_primarydoc.html"

        return {
            "filepath": filepath,
            "content": raw_html  # Still passing raw index HTML for now
        }

import requests

class SECFilingDownloader:
    def __init__(self, cik, user_agent):
        self.cik = cik  # original query CIK
        self.user_agent = user_agent
        self.data = None
        self.recent_filings = None

    def fetch_submissions(self):
        """Fetch submissions JSON from SEC."""
        url = f"https://data.sec.gov/submissions/CIK{self.cik.zfill(10)}.json"
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            self.data = response.json()
            print("✅ Data retrieved successfully.")
        else:
            raise Exception(f"Failed to fetch data: Status code {response.status_code}")

    def extract_recent_filings(self):
        """Extract recent filings from the fetched data."""
        if not self.data:
            raise Exception("No data loaded. Fetch data first.")

        self.recent_filings = self.data.get("filings", {}).get("recent", {})
        if not self.recent_filings:
            raise Exception("No recent filings found.")

        print(f"✅ {len(self.recent_filings.get('accessionNumber', []))} recent filings extracted.")

    def build_filing_urls(self, forms_filter=None):
        """
        Build filing URLs from recent filings.
        
        Args:
            forms_filter (list, optional): List of form types to include (e.g., ["8-K", "10-K"]).
        
        Returns:
            list of dicts: Each dict has accessionNumber, form, filingDate, primaryDocument, filing_url.
        """
        if self.recent_filings is None:
            raise Exception("No filings extracted. Run extract_recent_filings first.")

        results = []
        accession_numbers = self.recent_filings.get("accessionNumber", [])
        primary_documents = self.recent_filings.get("primaryDocument", [])
        filing_dates = self.recent_filings.get("filingDate", [])
        forms = self.recent_filings.get("form", [])

        for accession, document, date, form in zip(accession_numbers, primary_documents, filing_dates, forms):
            if forms_filter and form not in forms_filter:
                continue  # Skip forms not in the filter

            filing_url = self._construct_filing_url(accession, document)
            results.append({
                "accessionNumber": accession,
                "form": form,
                "filingDate": date,
                "primaryDocument": document,
                "filing_url": filing_url
            })

        print(f"✅ {len(results)} filings matched filter criteria." if forms_filter else f"✅ {len(results)} filings URLs built.")
        return results

    def _construct_filing_url(self, accession_number, primary_doc):
        """Helper function to build the SEC filing URL."""
        cik_from_accession = accession_number.split("-")[0].lstrip("0")  # Get first 10 digits, strip leading zeros
        accession_number_clean = accession_number.replace("-", "")
        return f"https://www.sec.gov/Archives/edgar/data/{cik_from_accession}/{accession_number_clean}/{primary_doc}"

# sec_downloader.py

import time
import requests
import os
from utils.file_saver import save_metadata_to_json  # NEW: for metadata saving

class SECDownloader:
    def __init__(self, cik: str = None, user_agent: str = None, request_delay_seconds: float = 1.0):
        """
        Initializes the SECDownloader with a user agent and polite request delay.
        Optionally accepts a CIK for the company (must be 10 digits after padding).
        """

        if not user_agent:
            raise ValueError("user_agent must be provided to SECDownloader.")

        self.user_agent = user_agent
        self.delay = request_delay_seconds
        self.last_request_time = None

        self.raw_cik = cik if cik else None  # ➡️ Store original raw cik
        self.cik = self._normalize_cik(cik) if cik else None  # ➡️ Normalized for metadata only
        self.data = None
        self.recent_filings = None

    def _normalize_cik(self, cik: str) -> str:
        """
        Left-pads the CIK to 10 digits.
        """
        return cik.zfill(10)

    def _throttle(self):
        """
        Ensures a polite delay between SEC requests.
        """
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)

    def _make_request(self, url: str) -> requests.Response:
        """
        Internal method to make a GET request with headers.
        """
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=10)
        return response

    def download_html(self, url: str) -> str:
        """
        Downloads raw HTML from the given SEC URL.
        Returns the HTML content as a string.
        """
        self._throttle()
        try:
            response = self._make_request(url)
            self.last_request_time = time.time()

            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Failed to fetch URL: {url}. Status code: {response.status_code}")

        except requests.RequestException as e:
            raise Exception(f"Network error occurred while fetching {url}: {str(e)}")

    def fetch_submissions(self):
        """
        Fetch submissions JSON from SEC for the stored CIK.
        Saves useful metadata to a JSON file.
        """
        if not self.cik:
            raise Exception("CIK is not set. Please set self.cik before fetching submissions.")

        self._throttle()
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"

        try:
            response = self._make_request(url)
            self.last_request_time = time.time()

            if response.status_code == 200:
                self.data = response.json()
                print("✅ Submissions data retrieved successfully.")
                metadata = self._extract_metadata()
                filepath = f"output/{self.cik}_metadata.json"
                save_metadata_to_json(metadata, filepath)
                print(f"✅ Metadata saved to {filepath}")
            else:
                raise Exception(f"Failed to fetch submissions: Status code {response.status_code}")

        except requests.RequestException as e:
            raise Exception(f"Network error occurred while fetching submissions: {str(e)}")

    def _extract_metadata(self) -> dict:
        """
        Extracts filing metadata from the submissions JSON.
        """
        if not self.data:
            raise Exception("No data loaded to extract metadata.")

        filings = self.data.get("filings", {}).get("recent", {})
        metadata = {
            "accessionNumber": filings.get("accessionNumber", []),
            "primaryDocument": filings.get("primaryDocument", []),
            "filingDate": filings.get("filingDate", []),
            "form": filings.get("form", []),
            "items": filings.get("items", []),       
            "isXBRL": filings.get("isXBRL", [])         
        }
        return metadata

    def extract_recent_filings(self):
        """
        Extract recent filings from previously fetched submissions JSON.
        """
        if not self.data:
            raise Exception("No data loaded. Fetch submissions first.")

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
            list of dicts: Each dict has accessionNumber, form, filingDate, primaryDocument, filing_url, items, isXBRL.
        """
        if self.recent_filings is None:
            raise Exception("No filings extracted. Run extract_recent_filings first.")

        results = []
        accession_numbers = self.recent_filings.get("accessionNumber", [])
        primary_documents = self.recent_filings.get("primaryDocument", [])
        filing_dates = self.recent_filings.get("filingDate", [])
        forms = self.recent_filings.get("form", [])
        items_list = self.recent_filings.get("items", [])
        is_xbrl_list = self.recent_filings.get("isXBRL", [])

        for idx, (accession, document, date, form) in enumerate(zip(accession_numbers, primary_documents, filing_dates, forms)):
            if forms_filter and form not in forms_filter:
                continue

            filing_url = self._construct_filing_url(accession, document)

            results.append({
                "accessionNumber": accession,
                "form": form,
                "filingDate": date,
                "primaryDocument": document,
                "filing_url": filing_url,
                "items": items_list[idx] if idx < len(items_list) else None,
                "isXBRL": is_xbrl_list[idx] if idx < len(is_xbrl_list) else None
            })

        print(f"✅ {len(results)} filings matched filter criteria." if forms_filter else f"✅ {len(results)} filings URLs built.")
        return results

    def _construct_filing_url(self, accession_number: str, primary_doc: str) -> str:
        """
        Build the SEC filing URL using raw (unpadded) CIK for the folder path.
        """
        accession_number_clean = accession_number.replace("-", "")
        return f"https://www.sec.gov/Archives/edgar/data/{self.raw_cik}/{accession_number_clean}/{primary_doc}"

# Example usage (remove or comment out if importing elsewhere)
if __name__ == "__main__":
    downloader = SECDownloader(
        cik="320193",
        user_agent="Safe Harbor Stocks kris@safeharborstocks.com",
        request_delay_seconds=0.2
    )
    try:
        downloader.fetch_submissions()
        downloader.extract_recent_filings()
        filings = downloader.build_filing_urls(forms_filter=["8-K", "10-K"])
        for filing in filings:
            print(filing)
    except Exception as e:
        print(f"Error: {e}")

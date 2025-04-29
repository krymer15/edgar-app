# collectors/submissions_collector.py

from collectors.base_collector import BaseCollector
from downloaders.sec_downloader import SECDownloader
from utils.url_builder import construct_submission_json_url, construct_primary_document_url

class SubmissionsCollector(BaseCollector):
    def __init__(self, user_agent: str):
        self.downloader = SECDownloader(user_agent=user_agent)

    def collect(self, cik: str, forms_filter: list = None) -> list:
        """
        Collect recent filings metadata for a given CIK.
        Optionally filter by form types (e.g., ["8-K", "10-K"]).

        Returns:
            List of dicts with filing metadata and download URLs.
        """
        normalized_cik = cik.zfill(10)
        url = construct_submission_json_url(normalized_cik)

        submissions_data = self.downloader.download_json(url)
        filings = submissions_data.get("filings", {}).get("recent", {})

        accession_numbers = filings.get("accessionNumber", [])
        primary_documents = filings.get("primaryDocument", [])
        filing_dates = filings.get("filingDate", [])
        forms = filings.get("form", [])
        items_list = filings.get("items", [])
        is_xbrl_list = filings.get("isXBRL", [])

        results = []
        for idx, (accession, primary_doc, date, form) in enumerate(zip(accession_numbers, primary_documents, filing_dates, forms)):
            if forms_filter and form not in forms_filter:
                continue

            filing_url = construct_primary_document_url(normalized_cik, accession, primary_doc)

            results.append({
                "accessionNumber": accession,
                "form": form,
                "filingDate": date,
                "primaryDocument": primary_doc,
                "filing_url": filing_url,
                "items": items_list[idx] if idx < len(items_list) else None,
                "isXBRL": is_xbrl_list[idx] if idx < len(is_xbrl_list) else None,
            })

        return results

# services/metadata_fetcher.py

from models.submissions import SubmissionsMetadata
from models.daily_index_metadata import DailyIndexMetadata

class MetadataFetcher:
    def __init__(self, db_session, source="submissions"):
        self.db_session = db_session
        self.source = source

    def get_urls_for_download(self, since_date=None):
        """Query the database for MAIN filing Detail URLs based on conditions (NOT Company Document URL)."""

        if self.source == "submissions":
            query = self.db_session.query(SubmissionsMetadata)
        elif self.source == "daily_index":
            query = self.db_session.query(DailyIndexMetadata)
        else:
            raise ValueError("Unknown source type for MetadataFetcher")

        if since_date:
            query = query.filter(DailyIndexMetadata.filing_date >= since_date) if self.source == "daily_index" else query.filter(SubmissionsMetadata.filing_date >= since_date)

        results = query.all()

        base_url = "https://www.sec.gov/Archives/edgar/data/"
        output = []

        if self.source == "submissions":
            for filing in results:
                cik_stripped = str(int(filing.cik))
                accession_clean = filing.accession_number.replace("-", "")
                if filing.primary_document:
                    url = f"{base_url}{cik_stripped}/{accession_clean}/{filing.primary_document}"
                    output.append(url)

        elif self.source == "daily_index":
            for filing in results:
                output.append({
                    "url": filing.filing_url, # SEC Filing Detail URL, not Primary Filing URL
                    "cik": filing.cik,
                    "form_type": filing.form_type,
                    "filing_date": filing.filing_date.isoformat() if filing.filing_date else None,
                    "accession_number": filing.accession_number
                })

        return output

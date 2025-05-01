# collectors/daily_index_collector.py

import requests
from collectors.base_collector import BaseCollector

class DailyIndexCollector(BaseCollector):
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    
    def collect(self, date: str):
        """
        Call, download and parse the SEC daily index file (crawler.idx) for a given date.

        Args:
            date (str): Filing date in YYYY-MM-DD format

        Returns:
            List[dict]: List of filing metadata dicts with keys:
                - cik
                - form_type
                - filing_date
                - filing_url
                - accession_number
        """
        year = date[:4]
        month = int(date[5:7])

        if 1 <= month <= 3:
            quarter = "QTR1"
        elif 4 <= month <= 6:
            quarter = "QTR2"
        elif 7 <= month <= 9:
            quarter = "QTR3"
        else:
            quarter = "QTR4"

        date_compact = date.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/{quarter}/crawler.{date_compact}.idx"


        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        lines = response.text.splitlines()

        # Skip SEC headers to the actual data (after long dashed line)
        start_index = 0
        for i, line in enumerate(lines):
            if set(line.strip()) == {"-"}:  # line is all dashes
                start_index = i + 1
                break

        parsed = []

        for line in lines[start_index:]:
            if not line.strip():
                continue

            # Parse line: CIK|Company Name|Form Type|Date Filed|Filename
            parts = line.split()
            if len(parts) < 5:
                continue  # Skip malformed

            company_name = " ".join(parts[:-4])
            form_type = parts[-4]
            cik = parts[-3]
            filing_date = parts[-2]
            filing_url = parts[-1]

            accession_number = filing_url.split("/")[-1].replace("-index.htm", "")

            parsed.append({
                "cik": cik.strip(),
                "form_type": form_type.strip(),
                "filing_date": filing_date.strip(),
                "filing_url": filing_url.strip(), # Only main filing detail URL, not the primary_document URL
                "accession_number": accession_number.strip()
            })

        print(f"🔎 Debug: {len(parsed)} filings parsed inside DailyIndexCollector")
        
        # Returns parsed dict of lists each containing metadata of each filing from the crawler.{date}.idx
        return parsed 

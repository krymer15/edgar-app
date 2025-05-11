# collectors/daily_index_collector.py

from datetime import datetime, date as dt_date
import requests
from collectors.base_collector import BaseCollector
from models.schemas.index_record_model import IndexRecordModel
from utils.report_logger import log_warn, log_debug

class DailyIndexCollector(BaseCollector):
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    
    def collect(self, date: str):
        """
        Call, download and parse the SEC daily index file (crawler.idx) for a given date.

        Args:
            date (str or datetime.date): Filing date in YYYY-MM-DD format or datetime.date

        Returns:
            List[dict]: List of filing metadata dicts with keys:
                - cik
                - form_type
                - filing_date
                - filing_url
                - accession_number
        """
        
        # Normalize string to datetime.date
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"[ERROR] Invalid date string format: '{date}' — expected YYYY-MM-DD")

        elif not isinstance(date, dt_date):
            raise TypeError(f"[ERROR] 'date' must be a str or datetime.date, got {type(date)}")
    
        year = str(date.year)
        month = date.month

        if 1 <= month <= 3:
            quarter = "QTR1"
        elif 4 <= month <= 6:
            quarter = "QTR2"
        elif 7 <= month <= 9:
            quarter = "QTR3"
        else:
            quarter = "QTR4"

        date_compact = date.strftime("%Y%m%d")
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

            try:
                record = IndexRecordModel(
                    cik=cik.strip(),
                    form_type=form_type.strip(),
                    filing_date=filing_date.strip(),
                    filing_url=filing_url.strip(),
                    accession_number=accession_number.strip()
                )
                parsed.append(record.model_dump())
            except Exception as e:
                log_warn(f"[SKIPPED] Malformed idx entry: {e}")
                continue

        log_debug(f"🔎 Parsed {len(parsed)} filings inside DailyIndexCollector")
        
        # Returns parsed dict of lists each containing metadata of each filing from the crawler.{date}.idx
        return parsed 

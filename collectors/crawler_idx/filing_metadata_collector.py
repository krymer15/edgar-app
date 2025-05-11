# collectors/crawler_idx/filing_metadata_collector.py

# NOTE: This inline download is kept simple for now.
# Future: Extract to CrawlerIdxDownloader if retry logic or parallel fetches are needed.

from datetime import date as dt_date, datetime
from typing import List, Union
import requests

from collectors.base_collector import BaseCollector
from models.dataclasses.filing_metadata import FilingMetadata
from utils.report_logger import log_warn
from parsers.idx.idx_parser import CrawlerIdxParser

class FilingMetadataCollector(BaseCollector):
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def collect(self, date: Union[str, dt_date], include_forms: list[str] = None) -> List[FilingMetadata]:
        """
        Download and parse the SEC daily index (crawler.idx) for a given date.
        Returns a list of FilingMetadata dataclass instances.
        """
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"[ERROR] Invalid date string format: '{date}' — expected YYYY-MM-DD")
        elif not isinstance(date, dt_date):
            raise TypeError(f"[ERROR] 'date' must be a str or datetime.date, got {type(date)}")

        # Determine quarter
        month = date.month
        quarter = f"QTR{(month - 1) // 3 + 1}"
        date_compact = date.strftime("%Y%m%d")
        year = date.strftime("%Y")

        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/{quarter}/crawler.{date_compact}.idx"
        headers = {"User-Agent": self.user_agent}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        lines = response.text.splitlines()
        try:
            all_records = CrawlerIdxParser.parse_lines(lines)
            if include_forms:
                all_records = [r for r in all_records if r.form_type in include_forms]
            return all_records
        except Exception as e:
            log_warn(f"[ERROR] Failed to parse crawler.idx: {e}")
            raise


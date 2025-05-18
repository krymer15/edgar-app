# collectors/crawler_idx/filing_metadata_collector.py

# NOTE: This inline download is kept simple for now.
# Future: Extract to CrawlerIdxDownloader if retry logic or parallel fetches are needed.

from datetime import date as dt_date, datetime
from typing import List, Union
import requests

from collections import defaultdict
from collectors.base_collector import BaseCollector
from models.dataclasses.filing_metadata import FilingMetadata
from utils.report_logger import log_warn, log_info
from utils.sgml_utils import download_sgml_for_accession, extract_issuer_cik_from_sgml
from parsers.idx.idx_parser import CrawlerIdxParser

class FilingMetadataCollector(BaseCollector):
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def collect(self, date: Union[str, dt_date], include_forms: list[str] = None, limit: int = None) -> List[FilingMetadata]:
        """
        Download and parse the SEC daily index (crawler.idx) for a given date.
        Returns a list of FilingMetadata dataclass instances.
        
        Args:
            date: Date string (YYYY-MM-DD) or datetime.date object
            include_forms: List of form types to include (e.g. ["10-K", "8-K"])
            limit: Maximum number of records to return
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
        
        log_info(f"[DEBUG] Downloading crawler.idx for {date_compact} from URL: {url}")
        # Set a timeout to avoid hanging indefinitely
        response = requests.get(url, headers=headers, timeout=30)
        log_info(f"[DEBUG] Download completed. Status code: {response.status_code}, Size: {len(response.text)//1024} KB")
        response.raise_for_status()

        lines = response.text.splitlines()
        log_info(f"[DEBUG] Parsing {len(lines)} lines from crawler.idx")
        try:
            all_records = CrawlerIdxParser.parse_lines(lines)
            log_info(f"[DEBUG] Parsed {len(all_records)} records from crawler.idx")
            if include_forms:
                all_records = [r for r in all_records if r.form_type in include_forms]
            
            # Apply limit early if provided (before expensive SGML downloads)
            if limit and limit > 0:
                all_records = all_records[:limit]
                log_info(f"Limited to {limit} records before processing")
                
            # Group records by accession number to identify potential duplicates
            records_by_accession = defaultdict(list)
            for record in all_records:
                records_by_accession[record.accession_number].append(record)
            
            # Process each group to handle multi-CIK filings
            final_records = []
            for accession, records in records_by_accession.items():
                # If only one record, no need for special handling
                if len(records) == 1:
                    final_records.append(records[0])
                    continue
                    
                # Multiple records with same accession - likely Form 4/3/5
                # Check if it's a form type that typically has issuer/reporting relationship
                if any(r.form_type in ["4", "3", "5", "13D", "13G", "13F-HR"] for r in records):
                    try:
                        # Download the SGML content using the first record
                        log_info(f"[DEBUG] Downloading SGML for multi-CIK accession: {accession}")
                        sgml_content = download_sgml_for_accession(
                            records[0].cik, 
                            accession, 
                            self.user_agent
                        )
                        log_info(f"[DEBUG] SGML download completed for {accession}")
                        
                        # Extract the issuer CIK
                        issuer_cik = extract_issuer_cik_from_sgml(sgml_content)
                        
                        if issuer_cik:
                            # Find the record that matches the issuer CIK
                            issuer_record = next((r for r in records if r.cik == issuer_cik), None)
                            
                            # If found, add it to final records
                            if issuer_record:
                                final_records.append(issuer_record)
                            else:
                                # If not found, just keep the first record
                                final_records.append(records[0])
                        else:
                            # If issuer CIK couldn't be extracted, use the first record
                            final_records.append(records[0])
                    except Exception as e:
                        # If any error occurs, fall back to using the first record
                        log_warn(f"Error processing multi-CIK filing {accession}: {e}")
                        final_records.append(records[0])
                else:
                    # For other form types, just use the first record
                    final_records.append(records[0])
            
            log_info(f"Handled {len(all_records) - len(final_records)} duplicate CIK records")
            log_info(f"[DEBUG] Final record count after processing: {len(final_records)}")
            return final_records
        except Exception as e:
            log_warn(f"[ERROR] Failed to parse crawler.idx: {e}")
            raise
            
        
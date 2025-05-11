# parsers/idx/idx_parser.py

from datetime import datetime
from typing import List
from models.dataclasses.filing_metadata import FilingMetadata
from utils.report_logger import log_warn

class CrawlerIdxParser:
    @staticmethod
    def parse_lines(lines: List[str]) -> List[FilingMetadata]:
        parsed = []

        # Locate start of data (line of dashes)
        start_index = 0
        for i, line in enumerate(lines):
            if set(line.strip()) == {"-"}:
                start_index = i + 1
                break

        for line in lines[start_index:]:
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) < 5:
                log_warn(f"[SKIPPED] Malformed line (too few parts): {line}")
                continue

            try:
                # Extract fields
                company_name = " ".join(parts[:-4])
                form_type = parts[-4]
                cik = parts[-3]
                filing_date_str = parts[-2]
                filing_url = parts[-1]

                # Parse date
                filing_date = datetime.strptime(filing_date_str.strip(), "%Y%m%d").date()

                # Extract accession number from URL
                accession_number = (
                    filing_url.split("/")[-1].replace("-index.htm", "").strip()
                )

                # Build FilingMetadata dataclass
                record = FilingMetadata(
                    cik=cik.strip(),
                    form_type=form_type.strip(),
                    filing_date=filing_date,
                    filing_url=filing_url.strip(),
                    accession_number=accession_number,
                )
                parsed.append(record)

            except Exception as e:
                log_warn(f"[SKIPPED] Error parsing line: {line} — {e}")
                continue

        return parsed

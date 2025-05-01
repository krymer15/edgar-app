# =============================================================================
# ARCHIVED MODULE — NOT ACTIVE IN PIPELINE
#
# This file was moved from /parsers/ and is no longer used in ingestion.
# Keep for potential reuse or reference during parser refactoring.
# =============================================================================


# parsers/daily_index_parser.py TODO See comment in def parse()
from parsers.base_parser import BaseParser

class DailyIndexParser(BaseParser):
    def parse(self, raw_metadata_list):
        """
        Transforms raw Daily Index filings into SubmissionsMetadata-ready dicts.
        THIS MODULE MAY NOT BE CURRENTLY USED! IT WAS TO PREPARE DAILY INDEX FILES TO MERGE WITH SAME DB AS SUBMISSIONS.
        THAT APPROACH WAS ABANDONED SINCE THE DATA STRUCTURES DIFFER TOO MUCH MISSING COMPANY_DOCUMENT ETC.
        """
        structured_records = []
        for filing in raw_metadata_list:
            structured = {
                "accession_number": filing.get("accession_number"),
                "cik": filing.get("cik"),
                "filing_date": filing.get("filing_date"),
                "form_type": filing.get("form_type"),
                "items": filing.get("items", []),
                "primary_document": filing.get("primary_document"),
                "document_description": filing.get("document_description"),
                "is_xbrl": False,
                "is_inline_xbrl": False,
                "acceptance_datetime": None,
            }
            structured_records.append(structured)

        return structured_records

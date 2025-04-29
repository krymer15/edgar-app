# parsers/daily_index_parser.py
from parsers.base_parser import BaseParser

class DailyIndexParser(BaseParser):
    def parse(self, raw_metadata_list):
        """
        Transforms raw Daily Index filings into SubmissionsMetadata-ready dicts.
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

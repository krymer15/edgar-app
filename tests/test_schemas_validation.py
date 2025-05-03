# tests/test_schemas_validation.py

from schemas import ParsedResultModel, IndexRecordModel
from pprint import pprint

def test_parsed_result_validation():
    # ✅ Simulated parsed result passed to writer
    parsed_result = {
        "metadata": {
            "cik": "0001084869",
            "accession_number": "0000921895-25-001190",
            "form_type": "4",
            "filing_date": "2025-04-28",
            "primary_document_url": "https://www.sec.gov/Archives/..."
        },
        "exhibits": [
            {
                "filename": "form413866005_04282025.xml",
                "description": "OWNERSHIP DOCUMENT",
                "type": "XML",
                "accessible": True
            }
        ]
    }

    model = ParsedResultModel(**parsed_result)
    pprint(model.dict())


def test_index_record_validation():
    # ✅ Simulated single record from crawler.idx
    idx_row = {
        "cik": "0001084869",
        "form_type": "4",
        "filing_date": "2025-04-28",
        "filing_url": "https://www.sec.gov/Archives/...",
        "accession_number": "0000921895-25-001190"
    }

    record = IndexRecordModel(**idx_row)
    pprint(record.dict())


if __name__ == "__main__":
    test_parsed_result_validation()
    test_index_record_validation()

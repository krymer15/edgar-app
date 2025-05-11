# tests/test_sgml_processor.py

import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from parsers.sgml_document_processor import SgmlDocumentProcessor

SAMPLE_FILE = "tests/samples/0000921895-25-001190.txt"

def load_sample():
    path = Path(SAMPLE_FILE)
    assert path.exists(), f"Sample file not found at {SAMPLE_FILE}"
    return path.read_text(encoding="utf-8")

@patch("parsers.sgml_document_processor.requests.get")
def test_sgml_document_processor_mocks_download(mock_get):
    sgml_contents = load_sample()

    # Mock HTTP response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = sgml_contents
    mock_get.return_value = mock_response

    processor = SgmlDocumentProcessor(user_agent="TestAgent/1.0")

    documents = processor.process(
        cik="0001084869",
        accession_number="0000921895-25-001190",
        form_type="4",
        filing_url="https://fake.sec.gov/fake-url.txt"  # not actually fetched
    )

    assert isinstance(documents, list)
    assert len(documents) > 0
    assert all(doc.accession_number == "0000921895-25-001190" for doc in documents)
    assert any(doc.is_primary for doc in documents)

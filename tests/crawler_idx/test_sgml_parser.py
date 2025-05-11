# tests/test_sgml_parser.py

from parsers.sgml_filing_parser import SgmlFilingParser
from pathlib import Path

SAMPLE_FILE = "tests/samples/0000921895-25-001190.txt"

def load_sample():
    path = Path(SAMPLE_FILE)
    assert path.exists(), f"Sample file not found at {SAMPLE_FILE}"
    return path.read_text(encoding="utf-8")

def test_parse_returns_documents():
    contents = load_sample()
    parser = SgmlFilingParser("0001084869", "0000921895-25-001190", "4")
    documents = parser.parse_to_documents(contents)
    assert isinstance(documents, list)
    assert len(documents) > 0

def test_primary_document_flag():
    contents = load_sample()
    parser = SgmlFilingParser("0001084869", "0000921895-25-001190", "4")
    documents = parser.parse_to_documents(contents)
    primaries = [doc for doc in documents if doc.is_primary]
    assert len(primaries) == 1
    assert primaries[0].filename.endswith(".xml")

def test_exhibit_and_data_support_flags():
    contents = load_sample()
    parser = SgmlFilingParser("0001084869", "0000921895-25-001190", "4")
    documents = parser.parse_to_documents(contents)

    for doc in documents:
        if doc.filename.endswith(".xml"):
            assert doc.is_data_support
            assert not doc.is_exhibit
        else:
            assert doc.is_exhibit
            assert not doc.is_data_support

def test_accessible_flag():
    contents = load_sample()
    parser = SgmlFilingParser("0001084869", "0000921895-25-001190", "4")
    documents = parser.parse_to_documents(contents)

    for doc in documents:
        assert doc.accessible is True  # sample file should contain no noise

def test_filename_and_source_url():
    contents = load_sample()
    parser = SgmlFilingParser("0001084869", "0000921895-25-001190", "4")
    documents = parser.parse_to_documents(contents)

    for doc in documents:
        assert doc.filename
        assert doc.source_url.startswith("https://www.sec.gov/Archives/")
        assert doc.accession_number == "0000921895-25-001190"

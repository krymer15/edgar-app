# tests/shared/test_raw_file_writer.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
import datetime
from writers.shared.raw_file_writer import RawFileWriter
from models.dataclasses.raw_document import RawDocument

@pytest.fixture
def temp_sgml_doc(tmp_path):
    return RawDocument(
        accession_number="0001234567-25-000001",
        cik="0001234567",
        document_type="10-K",
        filename="submission.txt",
        source_url="https://example.com/0001234567-25-000001.txt",
        source_type="sgml",
        content="This is a test SGML submission.\nLine 2 of content.",
        filing_date=datetime.date(2025, 5, 10),
        is_primary=True,
    ), tmp_path

def test_raw_file_writer_writes_file(temp_sgml_doc, monkeypatch):
    raw_doc, tmp_path = temp_sgml_doc

    # Redirect base_data_path to temp directory
    monkeypatch.setitem(
        __import__("utils.path_manager").path_manager.STORAGE_CONFIG,
        "base_data_path",
        str(tmp_path)
    )

    writer = RawFileWriter(file_type="sgml")
    output_path = writer.write(raw_doc)

    assert os.path.exists(output_path)
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "This is a test SGML submission" in content
        assert "Line 2" in content

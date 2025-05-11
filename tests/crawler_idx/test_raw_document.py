
import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

from dataclasses import asdict
import pytest
from models.dataclasses.raw_document import RawDocument

def test_raw_document_roundtrip():
    rd = RawDocument(
        accession_number="0001234567-21-000001",
        cik="0001234567",
        document_type="sgml",
        filename="0001234567-21-000001.txt",
        description="SGML submission",
        source_url="https://example.com/0001234567-21-000001.txt",
        source_type="sgml",
        is_primary=True,
        is_exhibit=False,
        is_data_support=False,
        accessible=True
    )
    data = asdict(rd)
    rd2 = RawDocument(**data)
    assert rd == rd2

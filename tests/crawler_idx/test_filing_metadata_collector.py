# tests/crawler_idx/test_filing_metadata_collector.py

'''Verifies .collect() integrates requests + parser'''

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch
from collectors.crawler_idx.filing_metadata_collector import FilingMetadataCollector
from models.dataclasses.filing_metadata import FilingMetadata

SAMPLE_DATE = "2024-05-01"
FIXTURE_PATH = Path("tests/fixtures/crawler_sample.idx")

# Patch requests.get to return sample idx text
class DummyResponse:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self): pass

@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    def fake_get(url, headers):
        return DummyResponse(FIXTURE_PATH.read_text(encoding="utf-8"))
    monkeypatch.setattr("requests.get", fake_get)

def test_collect_returns_filing_metadata_list():
    collector = FilingMetadataCollector(user_agent="test-agent")
    results = collector.collect(SAMPLE_DATE)

    assert isinstance(results, list)
    assert all(isinstance(r, FilingMetadata) for r in results)
    assert len(results) > 0

def test_collect_filters_by_include_forms():
    collector = FilingMetadataCollector(user_agent="test-agent")
    results = collector.collect(SAMPLE_DATE, include_forms=["10-K"])
    assert all(r.form_type == "10-K" for r in results)

def test_collect_handles_duplicate_accessions():
    """Test that collector properly handles multiple records with the same accession number."""
    # Patch the extract_issuer_cik_from_sgml function to return a known CIK
    with patch("utils.sgml_utils.extract_issuer_cik_from_sgml") as mock_extract:
        mock_extract.return_value = "0000123456"
        
        collector = FilingMetadataCollector(user_agent="test-agent")
        results = collector.collect(SAMPLE_DATE)
        
        # Check that duplicates are handled properly
        accession_counts = {}
        for r in results:
            accession_counts[r.accession_number] = accession_counts.get(r.accession_number, 0) + 1
            
        # There should be no duplicates in the results
        assert all(count == 1 for count in accession_counts.values())
# tests/crawler_idx/test_idx_parser.py

''' Verifies parsing from local .idx lines '''

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

from parsers.idx.idx_parser import CrawlerIdxParser
from models.dataclasses.filing_metadata import FilingMetadata

FIXTURE_PATH = Path("tests/fixtures/crawler_sample.idx")

def test_parse_lines_returns_expected_objects():
    lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
    results = CrawlerIdxParser.parse_lines(lines)

    assert isinstance(results, list)
    assert all(isinstance(r, FilingMetadata) for r in results)
    assert len(results) > 0

    first = results[0]
    assert first.cik.isdigit()
    assert isinstance(first.filing_date, date)
    assert first.filing_url.startswith(("https://", "http://"))
    assert first.accession_number in first.filing_url

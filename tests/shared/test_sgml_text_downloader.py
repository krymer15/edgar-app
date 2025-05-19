
import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from downloaders.sgml_downloader import SgmlDownloader
from models.dataclasses.sgml_text_document import SgmlTextDocument
from utils.path_manager import build_cache_path

def test_cache_read_write(tmp_path, monkeypatch):
    # Setup
    cik = "0000000000"
    accession = "20250101000001"
    expected_text = "SGML test content"

    # Monkeypatch cache path to tmp dir
    monkeypatch.setitem(
        os.environ, "APP_CONFIG", "tests/fixtures/app_config_test.yaml"
    )
    monkeypatch.setattr("utils.path_manager.STORAGE_CONFIG", {"base_data_path": str(tmp_path)})

    downloader = SgmlDownloader(user_agent="test-agent", use_cache=True)

    # Write and read from cache
    downloader.write_to_cache(cik, accession, expected_text, year="2025")
    assert downloader.is_cached(cik, accession, year="2025")
    content = downloader.read_from_cache(cik, accession, year="2025")
    assert content == expected_text

def test_download_sgml_uses_cache(monkeypatch):
    # Setup mock downloader
    cik, accession = "0000000000", "20250101000001"
    expected_doc = SgmlTextDocument(
        cik=cik,
        accession_number=accession,
        content="From cache"
    )

    class MockDownloader(SgmlDownloader):
        def __init__(self):
            super().__init__(user_agent="test", use_cache=True)
        def download_html(self, url):
            raise Exception("Should not call network")

    downloader = MockDownloader()
    monkeypatch.setattr(downloader, "read_from_cache", lambda *args: expected_doc.content)
    monkeypatch.setattr(downloader, "is_cached", lambda *args: True)
    monkeypatch.setattr(downloader, "is_stale", lambda path, max_age_seconds: False)  # Force cache to be valid

    result = downloader.download_sgml(cik, accession, year="2025")
    assert isinstance(result, SgmlTextDocument)
    assert result.cik == expected_doc.cik
    assert result.accession_number == expected_doc.accession_number
    assert result.content == expected_doc.content
    print(repr(result))
    
def test_url_construction_handles_dashes_consistently(monkeypatch):
    """Test that URL construction correctly handles accession numbers with and without dashes."""
    from utils.url_builder import construct_sgml_txt_url
    
    # Mock the construct_sgml_txt_url function to capture its inputs
    url_inputs = []
    original_construct_url = construct_sgml_txt_url
    
    def mock_construct_url(cik, accession_number):
        url_inputs.append((cik, accession_number))
        return original_construct_url(cik, accession_number)
    
    monkeypatch.setattr("utils.url_builder.construct_sgml_txt_url", mock_construct_url)
    
    # Create test downloader
    class TestDownloader(SgmlDownloader):
        def __init__(self):
            super().__init__(user_agent="test", use_cache=True)
        def download_html(self, url):
            return "MOCK CONTENT"
    
    downloader = TestDownloader()
    
    # Test with dashes in accession number
    cik = "0001234567"
    accession_with_dashes = "0001234567-25-012345"
    
    # This should pass the accession number with dashes to construct_sgml_txt_url
    downloader.download_sgml(cik, accession_with_dashes, year="2025")
    
    # The url_builder function should receive the accession number with dashes
    assert url_inputs[0][0] == cik
    assert url_inputs[0][1] == accession_with_dashes
    
    # Test with no dashes
    accession_no_dashes = "000123456725012345"
    downloader.download_sgml(cik, accession_no_dashes, year="2025")
    
    # The function should still receive the exact input (no dashes)
    assert url_inputs[1][0] == cik
    assert url_inputs[1][1] == accession_no_dashes
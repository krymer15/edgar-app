# tests/crawler_idx/test_filing_document_issuer_cik.py

import os, sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from models.dataclasses.filing_document_record import FilingDocumentRecord
from models.dataclasses.filing_document_metadata import FilingDocumentMetadata
from models.dataclasses.sgml_text_document import SgmlTextDocument
from parsers.sgml.indexers.sgml_document_indexer import SgmlDocumentIndexer
from utils.sgml_utils import extract_issuer_cik_from_sgml

def test_extract_issuer_cik_from_sgml():
    """Test extracting issuer CIK from SGML content."""
    # Create sample SGML content
    sgml_content = """
    <SEC-HEADER>
    <ISSUER>
    COMPANY CONFORMED NAME: TEST COMPANY INC
    CENTRAL INDEX KEY: 0001234567
    </ISSUER>
    </SEC-HEADER>
    """
    
    issuer_cik = extract_issuer_cik_from_sgml(sgml_content)
    assert issuer_cik == "0001234567"
    
    # Test with missing ISSUER section
    sgml_content_no_issuer = "<SEC-HEADER></SEC-HEADER>"
    issuer_cik = extract_issuer_cik_from_sgml(sgml_content_no_issuer)
    assert issuer_cik == ""

def test_sgml_document_indexer_extracts_issuer_cik():
    """Test that SgmlDocumentIndexer correctly extracts issuer CIK."""
    # Create mock SGML content
    sgml_content = """
    <SEC-HEADER>
    <ISSUER>
    COMPANY CONFORMED NAME: TEST COMPANY INC
    CENTRAL INDEX KEY: 0001234567
    </ISSUER>
    </SEC-HEADER>
    <DOCUMENT>
    <TYPE>4</TYPE>
    <SEQUENCE>1</SEQUENCE>
    <FILENAME>form4.xml</FILENAME>
    <DESCRIPTION>FORM 4</DESCRIPTION>
    </DOCUMENT>
    """
    
    with patch.object(SgmlDocumentIndexer, 'parse') as mock_parse:
        # Setup mock for parse method
        mock_parse.return_value = {
            "primary_document_url": "https://www.sec.gov/Archives/edgar/data/9876543210/000123456725000001/form4.xml",
            "exhibits": [
                {
                    "filename": "form4.xml",
                    "description": "FORM 4",
                    "type": "4",
                    "accessible": True,
                    "sequence": 1
                }
            ]
        }
        
        # Create indexer instance
        indexer = SgmlDocumentIndexer("9876543210", "0001234567-25-000001", "4")
        
        # Mock extract_issuer_info method
        with patch.object(indexer, 'extract_issuer_info') as mock_extract:
            mock_extract.return_value = {"issuer_cik": "0001234567", "issuer_name": "TEST COMPANY INC"}
            
            # Call index_documents
            documents = indexer.index_documents(sgml_content)
            
            # Verify
            assert len(documents) == 1
            assert documents[0].issuer_cik == "0001234567"
            assert documents[0].cik == "9876543210"  # Original CIK still preserved

@patch('collectors.crawler_idx.filing_documents_collector.SgmlDownloader')
@patch('collectors.crawler_idx.filing_documents_collector.SgmlDocumentIndexer')
@patch('utils.sgml_utils.extract_issuer_cik_from_sgml')
def test_filing_documents_collector_handles_issuer_cik(mock_extract_issuer, mock_indexer_cls, mock_downloader_cls):
    """Test that FilingDocumentsCollector properly handles issuer CIK."""
    from collectors.crawler_idx.filing_documents_collector import FilingDocumentsCollector
    from models.adapters.dataclass_to_orm import convert_parsed_doc_to_filing_doc
    from models.orm_models.filing_metadata import FilingMetadata
    
    # Mock database session
    mock_session = MagicMock()
    
    # Mock filing metadata record
    mock_record = MagicMock(spec=FilingMetadata)
    mock_record.cik = "9876543210"  # Reporting owner CIK
    mock_record.accession_number = "0001234567-25-000001"
    mock_record.form_type = "4"
    mock_record.filing_date = date(2025, 5, 15)
    
    # Fix the query chain to ensure records are returned
    query_mock = MagicMock()
    filter_mock = MagicMock()
    all_mock = MagicMock(return_value=[mock_record])
    
    mock_session.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    filter_mock.filter.return_value = filter_mock  # Support chained filters
    filter_mock.limit.return_value = filter_mock
    filter_mock.all.return_value = [mock_record]
    
    # Mock downloader
    mock_downloader = MagicMock()
    mock_downloader_cls.return_value = mock_downloader
    
    # Mock SGML document
    mock_sgml_doc = SgmlTextDocument(
        cik="9876543210",
        accession_number="0001234567-25-000001",
        content="Mock SGML content"
    )
    mock_downloader.download_sgml.return_value = mock_sgml_doc
    
    # Mock extract_issuer_cik_from_sgml
    mock_extract_issuer.return_value = "0001234567"  # Actual issuer CIK
    
    # Mock SgmlDocumentIndexer instance
    mock_indexer = MagicMock()
    mock_indexer_cls.return_value = mock_indexer
    
    # Create a FilingDocumentMetadata with issuer_cik
    doc_metadata = FilingDocumentMetadata(
        cik="9876543210",
        accession_number="0001234567-25-000001",
        form_type="4",
        filename="form4.xml",
        description="FORM 4",
        type="4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        is_primary=True,
        issuer_cik="0001234567"  # Set the issuer_cik
    )
    
    mock_indexer.index_documents.return_value = [doc_metadata]
    
    # Create collector with mock dependencies
    collector = FilingDocumentsCollector(
        db_session=mock_session,
        user_agent="test-agent",
        use_cache=False,
        downloader=mock_downloader
    )
    
    # Call collect method
    results = collector.collect(
        target_date="2025-05-15",
        include_forms=["4"]
    )
    
    # Verify results
    assert len(results) == 1
    assert results[0].cik == "9876543210"  # Original reporting owner CIK
    assert results[0].issuer_cik == "0001234567"  # Issuer CIK was added

def test_filing_document_metadata_includes_issuer_cik():
    """Test that FilingDocumentMetadata correctly includes the issuer_cik field."""
    # Create a FilingDocumentMetadata instance with issuer_cik
    metadata = FilingDocumentMetadata(
        cik="1234567890",
        accession_number="0001234567-25-000001",
        form_type="4",
        filename="form4.xml",
        description="FORM 4",
        type="4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        issuer_cik="0009876543"
    )
    
    # Verify the field is set correctly
    assert metadata.issuer_cik == "0009876543"
    
    # Test default value
    metadata_no_issuer = FilingDocumentMetadata(
        cik="1234567890",
        accession_number="0001234567-25-000001",
        form_type="4",
        filename="form4.xml",
        description="FORM 4",
        type="4",
        source_url="https://www.sec.gov/Archives/form4.xml"
    )
    
    assert metadata_no_issuer.issuer_cik is None

def test_filing_document_record_includes_issuer_cik():
    """Test that FilingDocumentRecord correctly includes the issuer_cik field."""
    # Create a FilingDocumentRecord instance with issuer_cik
    record = FilingDocumentRecord(
        cik="1234567890",
        accession_number="0001234567-25-000001",
        document_type="4",
        filename="form4.xml",
        description="FORM 4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        source_type="xml",
        issuer_cik="0009876543"
    )
    
    # Verify the field is set correctly
    assert record.issuer_cik == "0009876543"
    
    # Test default value
    record_no_issuer = FilingDocumentRecord(
        cik="1234567890",
        accession_number="0001234567-25-000001",
        document_type="4",
        filename="form4.xml",
        description="FORM 4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        source_type="xml"
    )
    
    assert record_no_issuer.issuer_cik is None

def test_convert_parsed_doc_to_filing_doc_preserves_issuer_cik():
    """Test that convert_parsed_doc_to_filing_doc preserves the issuer_cik field."""
    from models.adapters.dataclass_to_orm import convert_parsed_doc_to_filing_doc
    
    # Create a FilingDocumentMetadata instance with issuer_cik
    metadata = FilingDocumentMetadata(
        cik="1234567890",
        accession_number="0001234567-25-000001",
        form_type="4",
        filename="form4.xml",
        description="FORM 4",
        type="4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        issuer_cik="0009876543"
    )
    
    # Convert to FilingDocumentRecord
    record = convert_parsed_doc_to_filing_doc(metadata)
    
    # Verify the field is preserved
    assert record.issuer_cik == "0009876543"

def test_convert_filing_doc_to_orm_preserves_issuer_cik():
    """Test that convert_filing_doc_to_orm preserves the issuer_cik field."""
    from models.adapters.dataclass_to_orm import convert_filing_doc_to_orm
    
    # Create a FilingDocumentRecord instance with issuer_cik
    record = FilingDocumentRecord(
        cik="1234567890",
        accession_number="0001234567-25-000001",
        document_type="4",
        filename="form4.xml",
        description="FORM 4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        source_type="xml",
        issuer_cik="0009876543"
    )
    
    # Convert to ORM model
    orm_model = convert_filing_doc_to_orm(record)
    
    # Verify the field is preserved
    assert orm_model.issuer_cik == "0009876543"

@patch('collectors.crawler_idx.sgml_disk_collector.SgmlDownloader')
@patch('collectors.crawler_idx.sgml_disk_collector.RawFileWriter')
@patch('collectors.crawler_idx.sgml_disk_collector.build_raw_filepath_by_type')
@patch('collectors.crawler_idx.sgml_disk_collector.os.path.exists')
@patch('utils.sgml_utils.extract_issuer_cik_from_sgml')
def test_sgml_disk_collector_handles_issuer_cik(mock_extract_issuer, mock_path_exists, mock_build_path, mock_writer_cls, mock_downloader_cls):
    """Test that SgmlDiskCollector properly handles issuer CIK."""
    from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector
    
    # Mock path_exists to return False so we attempt to download
    mock_path_exists.return_value = False
    
    # Mock build_raw_filepath_by_type to return consistent paths
    mock_build_path.return_value = "/path/to/sgml.txt"
    
    # Mock database session
    mock_session = MagicMock()
    
    # Mock document record and associated filing metadata
    mock_filing = MagicMock()
    mock_filing.form_type = "4"
    mock_filing.filing_date = date(2025, 5, 15)
    
    mock_record = MagicMock()
    mock_record.cik = "9876543210"  # Reporting owner CIK
    mock_record.accession_number = "0001234567-25-000001"
    mock_record.document_type = "COMPLETE SUBMISSION"
    mock_record.source_type = "sgml"
    mock_record.source_url = "https://www.sec.gov/Archives/sgml.txt"
    mock_record.filename = "0001234567-25-000001.txt"
    mock_record.description = "Form 4"
    mock_record.is_primary = True
    mock_record.is_exhibit = False
    mock_record.is_data_support = False
    mock_record.accessible = True
    mock_record.filing = mock_filing
    
    # Setup query mock chain
    query_mock = MagicMock()
    join_mock = MagicMock()
    options_mock = MagicMock()
    filter_mock = MagicMock()
    all_mock = MagicMock(return_value=[mock_record])
    
    mock_session.query.return_value = query_mock
    query_mock.join.return_value = join_mock
    join_mock.options.return_value = options_mock
    options_mock.filter.return_value = filter_mock
    filter_mock.filter.return_value = filter_mock  # Support chained filters
    filter_mock.limit.return_value = filter_mock
    filter_mock.all.return_value = [mock_record]
    
    # Mock downloader and SGML document
    mock_downloader = MagicMock()
    mock_downloader_cls.return_value = mock_downloader
    
    mock_sgml_doc = SgmlTextDocument(
        cik="9876543210",
        accession_number="0001234567-25-000001",
        content="Mock SGML content"
    )
    mock_downloader.download_sgml.return_value = mock_sgml_doc
    
    # Mock extract_issuer_cik to return the issuer CIK
    mock_extract_issuer.return_value = "0001234567"  # Actual issuer CIK
    
    # Mock writer
    mock_writer = MagicMock()
    mock_writer_cls.return_value = mock_writer
    mock_writer.write.return_value = "/path/to/sgml.txt"
    
    # Create collector
    collector = SgmlDiskCollector(
        db_session=mock_session,
        user_agent="test-agent",
        use_cache=False,
        write_cache=False
    )
    
    # Call collect method
    written_paths = collector.collect(
        target_date="2025-05-15",
        include_forms=["4"]
    )
    
    # Verify results
    assert len(written_paths) == 1
    assert written_paths[0] == "/path/to/sgml.txt"
    
    # Verify that RawDocument was created with issuer_cik
    raw_doc_calls = mock_writer.write.call_args_list
    assert len(raw_doc_calls) == 1
    
    # Extract the RawDocument argument
    raw_doc = raw_doc_calls[0][0][0]
    assert raw_doc.cik == "0001234567"  # Should be updated to issuer CIK
    assert raw_doc.issuer_cik == "0001234567"

@patch('collectors.crawler_idx.sgml_disk_collector.SgmlDownloader')
@patch('collectors.crawler_idx.sgml_disk_collector.RawFileWriter')
@patch('collectors.crawler_idx.sgml_disk_collector.build_raw_filepath_by_type')
@patch('collectors.crawler_idx.sgml_disk_collector.os.path.exists')
@patch('utils.sgml_utils.extract_issuer_cik_from_sgml')
def test_sgml_disk_collector_falls_back_to_record_cik(mock_extract_issuer, mock_path_exists, mock_build_path, mock_writer_cls, mock_downloader_cls):
    """Test that SgmlDiskCollector falls back to record CIK when no issuer is found."""
    from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector
    
    # Mock path_exists to return False so we attempt to download
    mock_path_exists.return_value = False
    
    # Mock build_raw_filepath_by_type to return consistent paths
    mock_build_path.return_value = "/path/to/sgml.txt"
    
    # Mock database session
    mock_session = MagicMock()
    
    # Mock document record (same as above but for a 10-K which doesn't have issuer/reporter distinction)
    mock_filing = MagicMock()
    mock_filing.form_type = "10-K"
    mock_filing.filing_date = date(2025, 5, 15)
    
    mock_record = MagicMock()
    mock_record.cik = "0001234567"  # Company CIK
    mock_record.accession_number = "0001234567-25-000001"
    mock_record.document_type = "COMPLETE SUBMISSION"
    mock_record.source_type = "sgml"
    mock_record.source_url = "https://www.sec.gov/Archives/sgml.txt"
    mock_record.filename = "0001234567-25-000001.txt"
    mock_record.description = "Form 10-K"
    mock_record.is_primary = True
    mock_record.is_exhibit = False
    mock_record.is_data_support = False
    mock_record.accessible = True
    mock_record.filing = mock_filing
    
    # Setup query mock chain (same as above)
    query_mock = MagicMock()
    join_mock = MagicMock()
    options_mock = MagicMock()
    filter_mock = MagicMock()
    all_mock = MagicMock(return_value=[mock_record])
    
    mock_session.query.return_value = query_mock
    query_mock.join.return_value = join_mock
    join_mock.options.return_value = options_mock
    options_mock.filter.return_value = filter_mock
    filter_mock.filter.return_value = filter_mock
    filter_mock.limit.return_value = filter_mock
    filter_mock.all.return_value = [mock_record]
    
    # Mock downloader and SGML document
    mock_downloader = MagicMock()
    mock_downloader_cls.return_value = mock_downloader
    
    mock_sgml_doc = SgmlTextDocument(
        cik="0001234567",
        accession_number="0001234567-25-000001",
        content="Mock SGML content"
    )
    mock_downloader.download_sgml.return_value = mock_sgml_doc
    
    # Mock extract_issuer_cik to return empty string (no issuer section)
    mock_extract_issuer.return_value = ""
    
    # Mock writer (same as above)
    mock_writer = MagicMock()
    mock_writer_cls.return_value = mock_writer
    mock_writer.write.return_value = "/path/to/sgml.txt"
    
    # Create collector
    collector = SgmlDiskCollector(
        db_session=mock_session,
        user_agent="test-agent",
        use_cache=False,
        write_cache=False
    )
    
    # Call collect method
    written_paths = collector.collect(
        target_date="2025-05-15",
        include_forms=["10-K"]
    )
    
    # Verify results
    assert len(written_paths) == 1
    
    # Verify that RawDocument was created with correct CIK values
    raw_doc_calls = mock_writer.write.call_args_list
    raw_doc = raw_doc_calls[0][0][0]
    
    # For non-Form 4/3/5 filings, CIK and issuer_cik should be the same
    assert raw_doc.cik == "0001234567"
    assert raw_doc.issuer_cik == "0001234567"
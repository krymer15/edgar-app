# tests/crawler_idx/test_writer_issuer_cik.py

import os, sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from models.dataclasses.filing_document_record import FilingDocumentRecord
from models.orm_models.filing_document_orm import FilingDocumentORM

def test_filing_documents_writer_handles_issuer_cik():
    """Test that FilingDocumentsWriter correctly handles the issuer_cik field."""
    from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter
    
    # Create a mock DB session
    mock_session = MagicMock()
    
    # Create a FilingDocumentsWriter instance
    writer = FilingDocumentsWriter(db_session=mock_session)
    
    # Create a test record with issuer_cik
    record = FilingDocumentRecord(
        accession_number="0001234567-25-000001",
        cik="9876543210",  # Reporting owner CIK
        document_type="4",
        filename="form4.xml",
        description="FORM 4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        source_type="xml",
        issuer_cik="0001234567"  # Issuer CIK
    )
    
    # Mock the query to simulate no existing record
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = None
    
    # Call write_documents
    with patch('writers.crawler_idx.filing_documents_writer.convert_filing_doc_to_orm') as mock_convert:
        mock_orm = MagicMock(spec=FilingDocumentORM)
        mock_convert.return_value = mock_orm
        
        writer.write_documents([record])
        
        # Verify that convert_filing_doc_to_orm was called
        mock_convert.assert_called_once()
        
        # Verify that the ORM model was added to the session
        mock_session.add.assert_called_once_with(mock_orm)
        
        # Verify that commit was called
        mock_session.commit.assert_called_once()

def test_filing_documents_writer_updates_issuer_cik():
    """Test that FilingDocumentsWriter correctly updates the issuer_cik field."""
    from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter
    
    # Create a mock DB session
    mock_session = MagicMock()
    
    # Create a FilingDocumentsWriter instance
    writer = FilingDocumentsWriter(db_session=mock_session)
    
    # Create a test record with issuer_cik
    record = FilingDocumentRecord(
        accession_number="0001234567-25-000001",
        cik="9876543210",  # Reporting owner CIK
        document_type="4",
        filename="form4.xml",
        description="FORM 4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        source_type="xml",
        issuer_cik="0001234567"  # New issuer CIK
    )
    
    # Mock the query to simulate an existing record
    mock_existing = MagicMock(spec=FilingDocumentORM)
    mock_existing.description = "FORM 4"
    mock_existing.accessible = True
    mock_existing.issuer_cik = None  # Existing record has no issuer_cik
    
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = mock_existing
    
    # Call write_documents
    writer.write_documents([record])
    
    # Verify that the issuer_cik was updated
    assert mock_existing.issuer_cik == "0001234567"
    
    # Verify that commit was called
    mock_session.commit.assert_called_once()

def test_filing_documents_writer_skips_no_changes():
    """Test that FilingDocumentsWriter skips records when nothing has changed."""
    from writers.crawler_idx.filing_documents_writer import FilingDocumentsWriter
    
    # Create a mock DB session
    mock_session = MagicMock()
    
    # Create a FilingDocumentsWriter instance
    writer = FilingDocumentsWriter(db_session=mock_session)
    
    # Create a test record
    record = FilingDocumentRecord(
        accession_number="0001234567-25-000001",
        cik="9876543210",
        document_type="4",
        filename="form4.xml",
        description="FORM 4",
        source_url="https://www.sec.gov/Archives/form4.xml",
        source_type="xml",
        issuer_cik="0001234567"
    )
    
    # Mock the query to simulate an existing record with no changes needed
    mock_existing = MagicMock(spec=FilingDocumentORM)
    mock_existing.description = "FORM 4"
    mock_existing.accessible = True
    mock_existing.issuer_cik = "0001234567"  # Already has the same issuer_cik
    
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = mock_existing
    
    # Call write_documents
    with patch('writers.crawler_idx.filing_documents_writer.log_info') as mock_log:
        writer.write_documents([record])
        
        # Verify that skipped message was logged
        assert any("Skipped" in call_args[0][0] for call_args in mock_log.call_args_list)
        
    # Verify that commit was still called (for other potential records)
    mock_session.commit.assert_called_once()
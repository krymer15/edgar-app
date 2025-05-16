# tests/crawler_idx/test_issuer_cik_integration.py

import os, sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

def test_filing_documents_orchestrator_integration():
    """
    Integration test for FilingDocumentsOrchestrator with issuer_cik field.
    Mocks dependencies but tests the actual orchestration flow.
    """
    from orchestrators.crawler_idx.filing_documents_orchestrator import FilingDocumentsOrchestrator
    from models.dataclasses.filing_document_record import FilingDocumentRecord
    from models.database import get_db_session
    
    # Mock database session
    with patch('models.database.get_db_session') as mock_get_db_session:
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        
        # Mock ConfigLoader.load_config
        config = {
            "sec_downloader": {"user_agent": "test-agent"},
            "crawler_idx": {"include_forms_default": ["4"]}
        }
        
        with patch('config.config_loader.ConfigLoader.load_config', return_value=config):
            # Mock FilingDocumentsCollector
            with patch('orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsCollector') as mock_collector_cls:
                # Create mock collector instance
                mock_collector = MagicMock()
                mock_collector_cls.return_value = mock_collector
                
                # Make collect return a record with issuer_cik
                mock_record = FilingDocumentRecord(
                    accession_number="0001234567-25-000001",
                    cik="9876543210",  # Reporting owner CIK
                    document_type="4",
                    filename="form4.xml",
                    description="FORM 4",
                    source_url="https://www.sec.gov/Archives/form4.xml",
                    source_type="xml",
                    issuer_cik="0001234567"  # Issuer CIK
                )
                mock_collector.collect.return_value = [mock_record]
                
                # Mock FilingDocumentsWriter
                with patch('orchestrators.crawler_idx.filing_documents_orchestrator.FilingDocumentsWriter') as mock_writer_cls:
                    # Create mock writer instance
                    mock_writer = MagicMock()
                    mock_writer_cls.return_value = mock_writer
                    
                    # Create orchestrator
                    orchestrator = FilingDocumentsOrchestrator(
                        use_cache=False,
                        write_cache=False
                    )
                    
                    # Run orchestrator
                    orchestrator.run(
                        target_date="2025-05-15",
                        include_forms=["4"]
                    )
                    
                    # Verify that collector.collect was called with correct args
                    mock_collector.collect.assert_called_once_with(
                        target_date="2025-05-15",
                        limit=None,
                        accession_filters=None,
                        include_forms=["4"]
                    )
                    
                    # Verify that writer.write_documents was called with the record
                    mock_writer.write_documents.assert_called_once_with([mock_record])
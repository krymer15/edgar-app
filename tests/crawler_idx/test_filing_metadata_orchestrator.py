# tests/crawler_idx/test_filing_metadata_orchestrator.py

import unittest
from unittest.mock import patch, MagicMock
import sys, os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from orchestrators.crawler_idx.filing_metadata_orchestrator import FilingMetadataOrchestrator
from models.dataclasses.filing_metadata import FilingMetadata

class TestFilingMetadataOrchestrator(unittest.TestCase):
    
    @patch('orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataCollector')
    @patch('orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataWriter')
    @patch('orchestrators.crawler_idx.filing_metadata_orchestrator.ConfigLoader')
    def test_run_with_form_filtering(self, mock_config_loader, mock_writer, mock_collector):
        """Test running the orchestrator with form filtering"""
        # Setup mocks
        mock_config = {'sec_downloader': {'user_agent': 'TestAgent'}, 'crawler_idx': {'include_forms_default': ['10-K', '8-K']}}
        mock_config_loader.load_config.return_value = mock_config
        
        mock_collector_instance = MagicMock()
        mock_collector.return_value = mock_collector_instance
        
        mock_writer_instance = MagicMock()
        mock_writer.return_value = mock_writer_instance
        
        # Setup test data with correct structure
        test_records = [
            FilingMetadata(
                accession_number='0001234567-25-000001',
                cik='1234567',
                form_type='10-K',
                filing_date=date(2025, 5, 12)
            )
        ]
        mock_collector_instance.collect.return_value = test_records
        
        # Create orchestrator and run with default forms
        orchestrator = FilingMetadataOrchestrator()
        orchestrator.run(date_str='2025-05-12')
        
        # Verify collector was called with default forms
        mock_collector_instance.collect.assert_called_with('2025-05-12', include_forms=['10-K', '8-K'])
        
        # Verify writer was called with records
        mock_writer_instance.upsert_many.assert_called_with(test_records)
        
        # Reset mocks for next test
        mock_collector_instance.collect.reset_mock()
        mock_writer_instance.upsert_many.reset_mock()
        
        # Test with specific forms
        specific_forms = ['10-Q', 'S-1']
        orchestrator.run(date_str='2025-05-12', include_forms=specific_forms)
        
        # Verify collector was called with specific forms
        mock_collector_instance.collect.assert_called_with('2025-05-12', include_forms=specific_forms)
        
        # Verify writer was called with records
        mock_writer_instance.upsert_many.assert_called_with(test_records)
    
    @patch('orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataCollector')
    @patch('orchestrators.crawler_idx.filing_metadata_orchestrator.FilingMetadataWriter')
    @patch('orchestrators.crawler_idx.filing_metadata_orchestrator.ConfigLoader')
    def test_run_with_limit(self, mock_config_loader, mock_writer, mock_collector):
        """Test running the orchestrator with a record limit"""
        # Setup mocks
        mock_config = {'sec_downloader': {'user_agent': 'TestAgent'}, 'crawler_idx': {'include_forms_default': ['10-K', '8-K']}}
        mock_config_loader.load_config.return_value = mock_config
        
        mock_collector_instance = MagicMock()
        mock_collector.return_value = mock_collector_instance
        
        mock_writer_instance = MagicMock()
        mock_writer.return_value = mock_writer_instance
        
        # Setup test data with correct structure
        test_records = [
            FilingMetadata(
                accession_number='0001234567-25-000001',
                cik='1234567',
                form_type='10-K',
                filing_date=date(2025, 5, 12)
            ),
            FilingMetadata(
                accession_number='0007654321-25-000001',
                cik='7654321',
                form_type='8-K',
                filing_date=date(2025, 5, 12)
            )
        ]
        mock_collector_instance.collect.return_value = test_records
        
        # Create orchestrator and run with limit
        orchestrator = FilingMetadataOrchestrator()
        orchestrator.run(date_str='2025-05-12', limit=1)
        
        # Verify collector was called
        mock_collector_instance.collect.assert_called_with('2025-05-12', include_forms=['10-K', '8-K'])
        
        # Verify writer was called with limited records
        mock_writer_instance.upsert_many.assert_called_with([test_records[0]])


if __name__ == '__main__':
    unittest.main()
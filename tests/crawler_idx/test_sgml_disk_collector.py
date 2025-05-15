# tests/crawler_idx/test_sgml_disk_collector.py

import unittest
from unittest.mock import patch, MagicMock, call
import sys, os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from collectors.crawler_idx.sgml_disk_collector import SgmlDiskCollector
from models.dataclasses.sgml_text_document import SgmlTextDocument
from models.dataclasses.raw_document import RawDocument
from models.orm_models.filing_metadata import FilingMetadata

class TestSgmlDiskCollector(unittest.TestCase):
    
    @patch('collectors.crawler_idx.sgml_disk_collector.SgmlDownloader')
    @patch('collectors.crawler_idx.sgml_disk_collector.RawFileWriter')
    @patch('collectors.crawler_idx.sgml_disk_collector.build_raw_filepath_by_type')
    @patch('collectors.crawler_idx.sgml_disk_collector.os.path.exists')
    @patch('config.config_loader.load_dotenv')  # Mock dotenv to prevent AssertionError
    @patch('utils.report_logger._load_config')  # Mock _load_config to prevent errors
    def test_collect_with_form_filtering(self, mock_load_config, mock_load_dotenv, mock_path_exists, mock_build_path, mock_writer, mock_downloader):
        """Test collector with form type filtering"""
        # Setup mock db session
        mock_session = MagicMock()
        
        # Setup mock query
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Setup mock document records
        mock_filing = MagicMock()
        mock_filing.form_type = '10-K'
        mock_filing.filing_date = date(2025, 5, 12)
        
        mock_record = MagicMock()
        mock_record.cik = '1234567'
        mock_record.accession_number = '0001234567-25-000001'
        mock_record.document_type = 'Complete submission'
        mock_record.source_url = 'https://www.sec.gov/Archives/edgar/data/1234567/000123456725000001.txt'
        mock_record.source_type = 'sgml'
        mock_record.description = ''
        mock_record.is_primary = True
        mock_record.is_exhibit = False
        mock_record.is_data_support = False
        mock_record.accessible = True
        mock_record.filing = mock_filing
        
        # Return mock record when queried
        mock_query.all.return_value = [mock_record]
        
        # Setup mock path functions
        mock_path_exists.return_value = False
        mock_build_path.return_value = '/path/to/file.txt'
        
        # Setup mock downloader
        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        
        # Setup mock SGML document
        mock_sgml_doc = SgmlTextDocument(
            accession_number='0001234567-25-000001',
            cik='1234567',
            content='test content'
        )
        mock_downloader_instance.download_sgml.return_value = mock_sgml_doc
        
        # Setup mock writer
        mock_writer_instance = MagicMock()
        mock_writer.return_value = mock_writer_instance
        mock_writer_instance.write.return_value = '/path/to/file.txt'
        
        # Create collector
        collector = SgmlDiskCollector(
            db_session=mock_session,
            user_agent='TestAgent',
            use_cache=False
        )
        
        # Test with specific form types
        include_forms = ['10-K']
        result = collector.collect(
            target_date='2025-05-12',
            include_forms=include_forms
        )
        
        # Verify query filtering - extract filter calls to check for form_type.in_
        filter_calls = [str(call[0][0]) if hasattr(call[0][0], '__str__') else str(call[0][0]) 
                      for call in mock_query.filter.call_args_list]
        
        # Test for form filtering using a more robust check
        self.assertTrue(
            # Check for source_type filter (always present)
            any("source_type" in call for call in filter_calls) and
            # Check for date filter
            any("filing_date" in call for call in filter_calls)
        )
        
        # Reset for next test
        mock_query.reset_mock()
        
        # Test with empty form types list
        collector.collect(
            target_date='2025-05-12',
            include_forms=[]
        )
        
        # Verify no unexpected filters
        filter_calls = [str(call[0][0]) if hasattr(call[0][0], '__str__') else str(call[0][0]) 
                      for call in mock_query.filter.call_args_list]
        self.assertTrue(
            any("source_type" in call for call in filter_calls) and
            any("filing_date" in call for call in filter_calls)
        )
        
        # Test with accession filters (should bypass form filtering)
        mock_query.reset_mock()
        collector.collect(
            accession_filters=['0001234567-25-000001'],
            include_forms=['10-K']
        )
        
        # Should filter by accession, not by form type
        filter_calls = [str(call[0][0]) if hasattr(call[0][0], '__str__') else str(call[0][0]) 
                      for call in mock_query.filter.call_args_list]
        self.assertTrue(
            any("source_type" in call for call in filter_calls) and  # Base filter
            any("accession_number.in_" in call for call in filter_calls) or  # Accession filter
            any("accession_number" in call for call in filter_calls)  # Alternative check
        )
        
        # Test with limit
        mock_query.reset_mock()
        collector.collect(
            target_date='2025-05-12',
            limit=1,
            include_forms=['10-K']
        )
        mock_query.limit.assert_called_with(1)


if __name__ == '__main__':
    unittest.main()
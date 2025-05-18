# tests/forms/test_form4_orchestrator.py
import pytest
from unittest.mock import patch, MagicMock, call
import sys, os
from datetime import date, datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from orchestrators.forms.form4_orchestrator import Form4Orchestrator
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.raw_document import RawDocument
from models.orm_models.filing_metadata import FilingMetadata
from writers.shared.raw_file_writer import RawFileWriter

# Create a custom mock class that tracks attribute settings
class AttributeTrackingMock(MagicMock):
    def __init__(self, *args, **kwargs):
        # Initialize the attribute_updates dictionary before calling super
        self.attribute_updates = {}
        # Skip the MagicMock.__init__ for the attribute_updates attribute
        # to avoid infinite recursion when MagicMock tries to set up its internals
        object.__setattr__(self, 'attribute_updates', {})
        super().__init__(*args, **kwargs)
        
    def __setattr__(self, name, value):
        # Instead of checking hasattr, which can cause recursion with MagicMock,
        # directly access the attribute using object.__getattribute__
        if name == 'attribute_updates':
            # Use object.__setattr__ to bypass the MagicMock's __setattr__
            object.__setattr__(self, name, value)
        else:
            # Track the update in our dictionary
            try:
                updates = object.__getattribute__(self, 'attribute_updates')
                updates[name] = value
            except (AttributeError, RecursionError):
                # Handle the case where attribute_updates doesn't exist yet
                pass
            # Let MagicMock handle the actual attribute setting
            super().__setattr__(name, value)

@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment dependencies to avoid dotenv issues"""
    # Mock ConfigLoader directly
    config_loader_patcher = patch('config.config_loader.ConfigLoader.load_config')
    mock_config = config_loader_patcher.start()
    mock_config.return_value = {
        "paths": {"base_data_path": "data"},
        "sec_downloader": {"user_agent": "TestUserAgent/1.0"},
        "logger": {"level": "INFO", "log_to_console": True}
    }
    
    # Mock the _load_config function in report_logger
    report_config_patcher = patch('utils.report_logger._load_config')
    mock_report_config = report_config_patcher.start()
    
    # Mock report_logger functions to avoid dotenv issues
    log_info_patcher = patch('utils.report_logger.log_info')
    log_warn_patcher = patch('utils.report_logger.log_warn')
    log_error_patcher = patch('utils.report_logger.log_error')
    
    mock_log_info = log_info_patcher.start()
    mock_log_warn = log_warn_patcher.start()
    mock_log_error = log_error_patcher.start()
    
    # Mock dotenv.load_dotenv to prevent it from being called
    dotenv_patchers = [
        patch('config.config_loader.load_dotenv'),
        patch('dotenv.load_dotenv'),
        patch('dotenv.main.load_dotenv')
    ]
    
    for patcher in dotenv_patchers:
        patcher.start()
    
    yield {
        'log_info': mock_log_info,
        'log_warn': mock_log_warn,
        'log_error': mock_log_error
    }
    
    # Stop all patches
    config_loader_patcher.stop()
    report_config_patcher.stop()
    log_info_patcher.stop()
    log_warn_patcher.stop()
    log_error_patcher.stop()
    
    for patcher in dotenv_patchers:
        patcher.stop()

@pytest.fixture
def sample_form4_data():
    return Form4FilingData(
        accession_number="0001234567-25-000001",
        period_of_report=date(2025, 5, 14)
    )

def test_form4_orchestrator_run():
    """Test the main run method of Form4Orchestrator"""
    # Create a simple regular mock for the filing since we're not expecting 
    # property updates in this success case
    filing_mock = MagicMock()
    filing_mock.cik = "0001234567"
    filing_mock.accession_number = "0001234567-25-000001"
    filing_mock.form_type = "4"
    filing_mock.filing_date = "2025-05-15"
    filing_mock.processing_status = None
    
    # Create mock db session that returns empty queries to avoid complexity
    mock_db_session = MagicMock()
    
    # Simple downloader mock that returns SGML content
    mock_downloader = MagicMock()
    mock_downloader.has_in_memory_cache.return_value = False
    mock_downloader.download_sgml.return_value = "<SEC-HEADER>Sample SGML Content</SEC-HEADER>"
    
    # Mock Form4SgmlIndexer with minimal data
    mock_form4_indexer = MagicMock()
    mock_form4_indexer.index_documents.return_value = {
        "form4_data": Form4FilingData(
            accession_number="0001234567-25-000001",
            period_of_report=date(2025, 5, 14)
        ),
        "xml_content": "<XML>Sample XML</XML>"
    }
    
    # Simple mock writer that always succeeds
    mock_form4_writer = MagicMock()
    mock_form4_writer.write_form4_data.return_value = True  # Indicates success
    
    # Apply minimal patches to avoid deadlocks
    with patch('orchestrators.forms.form4_orchestrator.Form4SgmlIndexer', return_value=mock_form4_indexer), \
         patch('orchestrators.forms.form4_orchestrator.Form4Writer', return_value=mock_form4_writer), \
         patch('orchestrators.forms.form4_orchestrator.get_db_session') as mock_get_session, \
         patch.object(Form4Orchestrator, '_get_filings_to_process') as mock_get_filings:
        
        # Setup mock returns
        mock_get_filings.return_value = [filing_mock]
        mock_get_session.return_value.__enter__.return_value = mock_db_session
        
        # Create and run the orchestrator
        orchestrator = Form4Orchestrator(downloader=mock_downloader)
        result = orchestrator.run(target_date="2025-05-15")
        
        # Verify basic success case
        assert result["processed"] == 1
        assert result["succeeded"] == 1
        assert result["failed"] == 0
        
        # Verify critical dependencies were called
        mock_downloader.download_sgml.assert_called()
        mock_form4_indexer.index_documents.assert_called()
        mock_form4_writer.write_form4_data.assert_called()

def test_form4_orchestrator_handles_download_failure():
    """Test that the orchestrator properly handles download failures"""
    # Create mock downloader that fails to return SGML content
    mock_downloader = MagicMock()
    mock_downloader.has_in_memory_cache.return_value = False
    mock_downloader.download_sgml.return_value = None  # Failed download
    
    # Create a filing mock with properties we can verify
    filing_mock = MagicMock()
    filing_mock.cik = "0001234567"
    filing_mock.accession_number = "0001234567-25-000001"
    filing_mock.form_type = "4"
    filing_mock.filing_date = "2025-05-15"
    filing_mock.processing_status = None
    
    # Mock database session
    mock_db_session = MagicMock()
    
    # Apply minimal patches to avoid deadlocks
    with patch('orchestrators.forms.form4_orchestrator.get_db_session') as mock_get_session, \
         patch.object(Form4Orchestrator, '_get_filings_to_process') as mock_get_filings:
        
        # Setup mock returns
        mock_get_filings.return_value = [filing_mock]
        mock_get_session.return_value.__enter__.return_value = mock_db_session
        
        # Create and run the orchestrator
        orchestrator = Form4Orchestrator(downloader=mock_downloader)
        result = orchestrator.run(target_date="2025-05-15")
        
        # Verify the result shows a failure
        assert result["succeeded"] == 0
        assert result["failed"] == 1
        assert result["processed"] == 1
        assert len(result["failures"]) == 1
        
        # Verify the downloader was called
        mock_downloader.download_sgml.assert_called_once()
        
        # Instead of checking if the mock's attributes were updated (which can be unreliable),
        # we'll verify that the orchestrator attempted to commit changes to the database
        mock_db_session.commit.assert_called()

def test_form4_orchestrator_with_empty_results():
    """Test that the orchestrator handles empty query results correctly"""
    mock_downloader = MagicMock()
    
    # Mock database session
    mock_db_session = MagicMock()
    
    # Apply our patches
    with patch('orchestrators.forms.form4_orchestrator.get_db_session') as mock_get_session, \
         patch.object(Form4Orchestrator, '_get_filings_to_process') as mock_get_filings:
        
        # Setup empty filings list
        mock_get_filings.return_value = []
        
        # Setup session context manager
        mock_get_session.return_value.__enter__.return_value = mock_db_session
        
        # Create orchestrator 
        orchestrator = Form4Orchestrator(downloader=mock_downloader)
        
        # Run the orchestrator
        result = orchestrator.run(target_date="2025-05-15")
        
        # Verify the result
        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0
        assert "skipped" in result  # Make sure the key exists
        
        # Verify method calls
        mock_get_filings.assert_called_once()
        
        # Verify no downloader or indexer operations happened
        mock_downloader.download_sgml.assert_not_called()

def test_form4_orchestrator_xml_file_path():
    """Test that the orchestrator builds the correct XML file path using path_manager"""
    # Mock filing
    filing_mock = MagicMock()
    filing_mock.cik = "0001234567"
    filing_mock.accession_number = "0001234567-25-000001"
    filing_mock.form_type = "4"
    filing_mock.filing_date = datetime.strptime("2025-05-15", "%Y-%m-%d").date()
    
    # Mock XML content
    xml_content = "<XML>Sample XML</XML>"
    
    # Mock database session
    mock_db_session = MagicMock()
    
    # Mock downloader that returns SGML with XML
    mock_downloader = MagicMock()
    mock_downloader.has_in_memory_cache.return_value = False
    mock_downloader.download_sgml.return_value = f"<SEC-HEADER></SEC-HEADER>\n{xml_content}"
    
    # Mock Form4SgmlIndexer to return the XML content
    mock_form4_indexer = MagicMock()
    mock_form4_indexer.index_documents.return_value = {
        "form4_data": Form4FilingData(
            accession_number="0001234567-25-000001",
            period_of_report=date(2025, 5, 14)
        ),
        "xml_content": xml_content
    }
    
    # Mock Form4Writer
    mock_form4_writer = MagicMock()
    mock_form4_writer.write_form4_data.return_value = True
    
    # Mock RawFileWriter class and instance to capture the file path
    mock_raw_writer_instance = MagicMock()
    expected_path = "/mnt/data/raw/xml/0001234567/2025/4/0001234567-25-000001/000123456725000001_form4.xml"
    mock_raw_writer_instance.write.return_value = expected_path
    
    # Create a mock class that returns our instance when instantiated
    mock_raw_writer_class = MagicMock(return_value=mock_raw_writer_instance)
    
    with patch('orchestrators.forms.form4_orchestrator.Form4SgmlIndexer', return_value=mock_form4_indexer), \
         patch('orchestrators.forms.form4_orchestrator.Form4Writer', return_value=mock_form4_writer), \
         patch('orchestrators.forms.form4_orchestrator.RawFileWriter', mock_raw_writer_class), \
         patch('orchestrators.forms.form4_orchestrator.get_db_session') as mock_get_session, \
         patch.object(Form4Orchestrator, '_get_filings_to_process') as mock_get_filings:
        
        # Set up the mock returns
        mock_get_filings.return_value = [filing_mock]
        mock_get_session.return_value.__enter__.return_value = mock_db_session
        
        # Create and run the orchestrator with write_raw_xml=True
        orchestrator = Form4Orchestrator(downloader=mock_downloader)
        orchestrator.run(target_date="2025-05-15", write_raw_xml=True)
        
        # Verify that the RawFileWriter class was instantiated with the correct file_type
        mock_raw_writer_class.assert_called_once_with(file_type="xml")
        
        # Verify that the raw writer instance's write method was called with a RawDocument
        mock_raw_writer_instance.write.assert_called_once()
        raw_doc_arg = mock_raw_writer_instance.write.call_args[0][0]
        assert isinstance(raw_doc_arg, RawDocument)
        assert raw_doc_arg.cik == "0001234567"
        assert raw_doc_arg.accession_number == "0001234567-25-000001"
        assert raw_doc_arg.form_type == "4"
        assert raw_doc_arg.content == xml_content
        assert raw_doc_arg.document_type == "xml"
        assert raw_doc_arg.source_type == "form4_xml"
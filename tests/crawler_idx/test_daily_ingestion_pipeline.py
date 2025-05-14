# tests/crawler_idx/test_daily_ingestion_pipeline.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

from unittest.mock import patch, MagicMock
from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionPipeline

def test_pipeline_invokes_all_stages():
    with patch("orchestrators.crawler_idx.daily_ingestion_pipeline.FilingMetadataOrchestrator") as MockMeta, \
         patch("orchestrators.crawler_idx.daily_ingestion_pipeline.FilingDocumentsOrchestrator") as MockDocs, \
         patch("orchestrators.crawler_idx.daily_ingestion_pipeline.SgmlDiskOrchestrator") as MockSgml:

        mock_meta = MockMeta.return_value
        mock_docs = MockDocs.return_value
        mock_sgml = MockSgml.return_value

        pipeline = DailyIngestionPipeline(use_cache=True)
        pipeline.run("2025-05-12", limit=3)

        mock_meta.run.assert_called_once_with(date_str="2025-05-12", limit=3)
        mock_docs.run.assert_called_once_with(target_date="2025-05-12", limit=3)
        mock_sgml.run.assert_called_once_with(target_date="2025-05-12", limit=3)

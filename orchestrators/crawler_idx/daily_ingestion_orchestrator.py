# Calls both above and tracks/report status

from orchestrators.base_orchestrator import BaseOrchestrator
from orchestrators.filing_metadata_orchestrator import FilingMetadataOrchestrator
from orchestrators.filing_documents_orchestrator import FilingDocumentsOrchestrator

class DailyIngestionOrchestrator(BaseOrchestrator):
    def __init__(self, user_agent: str):
        self.meta_orch = FilingMetadataOrchestrator(user_agent) # populates filing_metadata
        self.docs_orch = FilingDocumentsOrchestrator()  # extracts <DOCUMENT>s into filing_documents

    def orchestrate(self, date_str: str, skip_meta=False, skip_docs=False, limit=None):
        if not skip_meta:
            self.meta_orch.run(date_str, limit=limit)
        if not skip_docs:
            self.docs_orch.run(date_str, limit=limit)

    def run(self, date_str: str, skip_meta=False, skip_docs=False, limit=None):
        return self.orchestrate(date_str, skip_meta=skip_meta, skip_docs=skip_docs, limit=limit)
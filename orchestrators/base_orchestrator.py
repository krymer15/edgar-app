# orchestrators/base_orchestrator.py
from abc import ABC, abstractmethod

class BaseOrchestrator(ABC):
    @abstractmethod
    def orchestrate(self, *args, **kwargs):
        """Manage the ingestion flow across collector, downloader, parser, writer."""
        pass

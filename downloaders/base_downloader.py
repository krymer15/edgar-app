# downloaders/base_downloader.py
from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    @abstractmethod
    def download(self, *args, **kwargs):
        """Download full raw filing documents."""
        pass

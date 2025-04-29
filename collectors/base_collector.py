# collectors/base_collector.py
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    @abstractmethod
    def collect(self, *args, **kwargs):
        """Collect raw filing metadata or references."""
        pass

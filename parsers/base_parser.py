# parsers/base_parser.py
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, *args, **kwargs):
        """Parse raw filings into structured clean outputs."""
        pass

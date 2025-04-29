# writers/base_writer.py

from abc import ABC, abstractmethod

class BaseWriter(ABC):
    def __init__(self, db_session):
        self.db_session = db_session

    @abstractmethod
    def write_metadata(self, *args, **kwargs):
        """Write collected filing metadata to storage."""
        pass

    @abstractmethod
    def write_content(self, *args, **kwargs):
        """Write parsed and structured filing content to storage."""
        pass

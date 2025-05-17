# parsers/sgml/indexers/sgml_indexer_factory.py
from typing import Dict, Type
from parsers.sgml.indexers.sgml_document_indexer import SgmlDocumentIndexer
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from utils.report_logger import log_info

class SgmlIndexerFactory:
    # Registry of form types to indexer classes
    _indexers: Dict[str, Type[SgmlDocumentIndexer]] = {
        "4": Form4SgmlIndexer,
        # Add more form types here as they are implemented
    }

    @classmethod
    def create_indexer(cls, form_type: str, cik: str, accession_number: str) -> SgmlDocumentIndexer:
        """
        Factory method to create the appropriate SGML indexer based on form_type.

        Args:
            form_type: SEC form type (e.g., '4', '10-K')
            cik: Company CIK number
            accession_number: SEC accession number

        Returns:
            An appropriate SGML indexer instance
        """
        # Normalize form type
        normalized_form = cls._normalize_form_type(form_type)

        # Check if we have a specialized indexer
        if normalized_form in cls._indexers:
            log_info(f"Using specialized indexer for form type '{form_type}'")
            return cls._indexers[normalized_form](cik, accession_number)

        # Default indexer for other form types
        log_info(f"Using default indexer for form type '{form_type}'")
        return SgmlDocumentIndexer(cik, accession_number, form_type)

    @staticmethod
    def _normalize_form_type(form_type: str) -> str:
        """Normalize form type for consistent matching"""
        # Remove "form" prefix, spaces, hyphens, and make lowercase
        normalized = form_type.lower().replace("form", "").replace(" ", "").replace("-", "")
        # Remove /A suffix for amended filings
        normalized = normalized.split("/")[0]
        return normalized.strip()

    @classmethod
    def register_indexer(cls, form_type: str, indexer_class: Type[SgmlDocumentIndexer]) -> None:
        """Register a new indexer class for a form type"""
        normalized = cls._normalize_form_type(form_type)
        cls._indexers[normalized] = indexer_class
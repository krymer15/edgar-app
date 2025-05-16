# collectors/crawler_idx/filing_documents_collector.py

# Role: Ties metadata → downloader → parser → adapter

from typing import List, Optional, Union
from sqlalchemy.orm import Session

from models.orm_models.filing_metadata import FilingMetadata
from models.dataclasses.filing_document_record import FilingDocumentRecord
from models.dataclasses.sgml_text_document import SgmlTextDocument
from models.adapters.dataclass_to_orm import convert_parsed_doc_to_filing_doc

from parsers.sgml.indexers.sgml_document_indexer import SgmlDocumentIndexer
from downloaders.sgml_downloader import SgmlDownloader
from utils.report_logger import log_info, log_error, log_warn
from utils.sgml_utils import extract_issuer_cik_from_sgml

class FilingDocumentsCollector:
    """Collects filing document records from SGML files"""
    def __init__(self, db_session: Session, user_agent: str, use_cache: bool = True, write_cache: bool = True, downloader: SgmlDownloader = None):
        self.db_session = db_session
        self.use_cache = use_cache
        self.write_cache = write_cache
        self.downloader = downloader or SgmlDownloader(user_agent=user_agent, use_cache=use_cache)

    def collect(
        self, 
        target_date: str = None, 
        limit: int = None, 
        accession_filters: list[str] = None,
        include_forms: Optional[List[str]] = None
    ) -> List[FilingDocumentRecord]:
        """
        Collects filing document records, optionally filtered by form types.
        
        Args:
            target_date: Target date string in YYYY-MM-DD format
            limit: Maximum number of records to retrieve
            accession_filters: List of specific accession numbers to process
            include_forms: List of form types to include (e.g., ["10-K", "8-K"])
            
        Returns:
            List of FilingDocumentRecord objects
        """        
        query = self.db_session.query(FilingMetadata)

        if accession_filters:
            query = query.filter(FilingMetadata.accession_number.in_(accession_filters))
        elif target_date:
            query = query.filter(FilingMetadata.filing_date == target_date)

            # Apply form type filtering if specified and not using accession filters
            if include_forms:
                log_info(f"[DOCS] Filtering documents by form types: {include_forms}")
                query = query.filter(FilingMetadata.form_type.in_(include_forms))

        if limit and not accession_filters:
            query = query.limit(limit)

        records = query.all()

        if include_forms:
            log_info(f"[DOCS] Processing {len(records)} records for form types: {include_forms}")
        else:
            log_info(f"[DOCS] Processing {len(records)} records")

        all_docs = []
        for record in records:
            try:
                # First attempt download using the record CIK
                year = str(record.filing_date.year)
                sgml_doc = None
                issuer_cik = None
                
                try:
                    sgml_doc = self.downloader.download_sgml(
                        record.cik, 
                        record.accession_number,
                        year=year,
                        write_cache=self.write_cache
                    )
                    
                    # For forms that may have issuer/reporting relationship
                    if record.form_type in ["3", "4", "5", "13D", "13G", "13F-HR", "144"]:
                        # Check if the CIK in the record is actually the issuer
                        issuer_cik = extract_issuer_cik_from_sgml(sgml_doc.content)
                        if issuer_cik and issuer_cik != record.cik:
                            log_info(f"Record CIK {record.cik} is not the issuer ({issuer_cik}) for {record.accession_number}. Retrying download with issuer CIK.")
                            # Retry download with issuer CIK
                            sgml_doc = self.downloader.download_sgml(
                                issuer_cik,
                                record.accession_number,
                                year=year,
                                write_cache=self.write_cache
                            )
                        else:
                            # If no issuer CIK was found or it matches the record CIK
                            if not issuer_cik:
                                issuer_cik = record.cik  # Default to record CIK
                    else:
                        # For regular forms, both CIKs are the same
                        issuer_cik = record.cik
                except Exception as e:
                    # If download fails with record CIK, we may be dealing with a reporting owner CIK
                    # Try to reconstruct the canonical URL with a common issuer CIK pattern
                    log_warn(f"Failed to download with CIK {record.cik} for {record.accession_number}, error: {e}")
                    # Let this propagate to the outer exception handler
                    raise
                    
                # Continue with parsing
                parser = SgmlDocumentIndexer(record.cik, record.accession_number, record.form_type)
                parsed_metadata = parser.index_documents(sgml_doc.content)
                
                # Add issuer_cik to the parsed metadata if not already set
                for doc in parsed_metadata:
                    if doc.issuer_cik is None:
                        doc.issuer_cik = issuer_cik
                
                filing_docs = [convert_parsed_doc_to_filing_doc(doc) for doc in parsed_metadata]
                all_docs.extend(filing_docs)
            except Exception as e:
                log_error(f"Failed to process {record.accession_number}: {e}")

        return all_docs
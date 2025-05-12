# collectors/crawler_idx/filing_documents_collector.py

# Role: Ties metadata → downloader → parser → adapter

from typing import List
from sqlalchemy.orm import Session

from models.orm_models.filing_metadata import FilingMetadata
from models.dataclasses.filing_document_record import FilingDocumentRecord
from models.dataclasses.sgml_text_document import SgmlTextDocument
from models.adapters.dataclass_to_orm import convert_parsed_doc_to_filing_doc

from parsers.sgml.indexers.sgml_document_indexer import SgmlDocumentIndexer
from downloaders.sgml_downloader import SgmlDownloader
from utils.report_logger import log_info, log_error

class FilingDocumentsCollector:
    def __init__(self, db_session: Session, user_agent: str, use_cache: bool = True):
        self.db_session = db_session
        self.downloader = SgmlDownloader(user_agent=user_agent, use_cache=use_cache)

    def collect(self, target_date: str) -> List[FilingDocumentRecord]:
        records = (
            self.db_session.query(FilingMetadata)
            .filter(FilingMetadata.filing_date == target_date)
            .all()
        )

        all_docs = []
        for record in records:
            try:
                sgml_doc: SgmlTextDocument = self.downloader.download_sgml(record.cik, record.accession_number)
                parser = SgmlDocumentIndexer(record.cik, record.accession_number, record.form_type)
                parsed_metadata = parser.index_documents(sgml_doc.content)
                filing_docs = [convert_parsed_doc_to_filing_doc(doc) for doc in parsed_metadata]
                all_docs.extend(filing_docs)
            except Exception as e:
                log_error(f"❌ Failed to process {record.accession_number}: {e}")

        return all_docs

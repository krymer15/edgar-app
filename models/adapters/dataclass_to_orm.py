''' 
Role:  
- handles both Parsed → FilingDocDC and FilingDocDC → ORM
- handles FilingMetadataDC -> FilingMetadataORM
'''

from models.dataclasses.filing_metadata import FilingMetadata as FilingMetadataDC
from models.orm_models.filing_metadata import FilingMetadata as FilingMetadataORM

from models.dataclasses.filing_document import FilingDocument as FilingDocDC
from models.orm_models.filing_documents import FilingDocument as FilingDocORM

from models.dataclasses.parsed_document import ParsedDocument

def convert_to_orm(dataclass_obj: FilingMetadataDC) -> FilingMetadataORM:
    return FilingMetadataORM(
        accession_number=dataclass_obj.accession_number,
        cik=dataclass_obj.cik,
        form_type=dataclass_obj.form_type,
        filing_date=dataclass_obj.filing_date,
        filing_url=dataclass_obj.filing_url,
    )

def convert_filing_doc_to_orm(dc: FilingDocDC) -> FilingDocORM:
    return FilingDocORM(
        accession_number=dc.accession_number,
        cik=dc.cik,
        document_type=dc.document_type,
        filename=dc.filename,
        description=dc.description,
        source_url=dc.source_url,
        source_type=dc.source_type,
        is_primary=dc.is_primary,
        is_exhibit=dc.is_exhibit,
        is_data_support=dc.is_data_support,
        accessible=dc.accessible,
    )

def convert_parsed_doc_to_filing_doc(parsed: ParsedDocument) -> FilingDocDC:
    return FilingDocDC(
        accession_number=parsed.accession_number,
        cik=parsed.cik,
        document_type=parsed.type,
        filename=parsed.filename,
        description=parsed.description,
        source_url=parsed.source_url,
        source_type=parsed.source_type,
        is_primary=parsed.is_primary,
        is_exhibit=parsed.is_exhibit,
        is_data_support=parsed.is_data_support,
        accessible=parsed.accessible,
    )
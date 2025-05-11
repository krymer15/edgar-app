from models.dataclasses.filing_metadata import FilingMetadata as FilingMetadataDC
from models.orm_models.filing_metadata import FilingMetadata as FilingMetadataORM

def convert_to_orm(dataclass_obj: FilingMetadataDC) -> FilingMetadataORM:
    return FilingMetadataORM(
        accession_number=dataclass_obj.accession_number,
        cik=dataclass_obj.cik,
        form_type=dataclass_obj.form_type,
        filing_date=dataclass_obj.filing_date,
        filing_url=dataclass_obj.filing_url,
    )

# models/parsed_result_model.py

from typing import List, Optional
from pydantic import BaseModel, Field


class ExhibitModel(BaseModel):
    filename: str
    description: Optional[str]
    type: Optional[str]
    accessible: Optional[bool] = True


class ParsedMetadataModel(BaseModel):
    cik: str
    accession_number: str
    form_type: str
    filing_date: str
    primary_doc_url: Optional[str]


class ParsedResultModel(BaseModel):
    metadata: ParsedMetadataModel
    exhibits: List[ExhibitModel]

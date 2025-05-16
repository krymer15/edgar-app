# tests/crawler_idx/test_dataclass_to_orm.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from unittest.mock import MagicMock, patch
from models.dataclasses.filing_metadata import FilingMetadata as FilingMetadataDC
from models.adapters.dataclass_to_orm import convert_to_orm
from datetime import datetime, date

def test_convert_to_orm():
    # Create a dataclass instance
    dc = FilingMetadataDC(
        accession_number="0001234567-21-000001",
        cik="0001234567",
        form_type="8-K",
        filing_date=date(2021, 7, 1),
        filing_url="https://example.com/filing"
    )
    
    # Convert to ORM
    orm = convert_to_orm(dc)
    
    # Verify fields are mapped correctly
    assert orm.accession_number == dc.accession_number
    assert orm.cik == dc.cik
    assert orm.form_type == dc.form_type
    assert orm.filing_date == dc.filing_date
    assert orm.filing_url == dc.filing_url
    
    # Verify the ORM object has no removed fields
    assert not hasattr(orm, "issuer_cik")
    assert not hasattr(orm, "is_issuer")
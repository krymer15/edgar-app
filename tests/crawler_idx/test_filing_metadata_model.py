# tests/test_filing_metadata_model.py

import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from datetime import date
from models.dataclasses.filing_metadata import FilingMetadata as DM
from models.orm_models.filing_metadata import FilingMetadata as ORM
from sqlalchemy import inspect

def test_dataclass_roundtrip():
    dm = DM(
        accession_number="0001234567-21-000001",
        cik="0001234567",
        form_type="8-K",
        filing_date=date(2021, 7, 1),
        filing_url="https://www.sec.gov/Archives/edgar/data/1234567/000123456721000001/filing.htm"
    )
    data = dm.__dict__
    dm2 = DM(**data)
    assert dm == dm2

def test_orm_mapping_matches_ddl():
    mapper = inspect(ORM)
    cols = {c.key: c for c in mapper.columns}

    # primary key
    assert cols["accession_number"].primary_key

    # required columns exist
    for field in ["cik", "form_type", "filing_date", "filing_url"]:
        assert field in cols

    # verify removed columns don't exist
    assert "issuer_cik" not in cols
    assert "is_issuer" not in cols

    # types
    assert str(cols["filing_date"].type) == "DATE"
    assert "TIMESTAMP" in str(cols["created_at"].type).upper()
    assert "TIMESTAMP" in str(cols["updated_at"].type).upper()

    # index on cik
    indexes = {idx.columns.keys()[0] for idx in mapper.tables[0].indexes}
    assert "cik" in indexes

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])

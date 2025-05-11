
import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import pytest
from sqlalchemy import inspect
from models.orm_models.filing_metadata import FilingMetadata
from models.orm_models.filing_documents import FilingDocument

def test_orm_mapping_matches_ddl():
    mapper = inspect(FilingDocument)
    cols = {c.key: c for c in mapper.columns}

    # Primary key
    assert cols["id"].primary_key

    # Foreign key to filing_metadata.accession_number
    fks = cols["accession_number"].foreign_keys
    assert any("filing_metadata.accession_number" in str(fk.column) for fk in fks)

    # Required fields exist
    for field in [
        "cik", "document_type", "filename", "description",
        "source_url", "source_type", "is_primary",
        "is_exhibit", "is_data_support", "accessible"
    ]:
        assert field in cols

    # Defaults / server defaults
    assert "CURRENT_TIMESTAMP" in str(cols["created_at"].server_default.arg)
    assert "CURRENT_TIMESTAMP" in str(cols["updated_at"].server_default.arg)

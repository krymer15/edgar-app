# utils/xml_backfill_utils.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.parsed_sgml_metadata import ParsedSgmlMetadata
from models.exhibit_metadata import ExhibitMetadata
from models.daily_index_metadata import DailyIndexMetadata
from models.xml_metadata import XmlMetadata
from archive.writers.xml_metadata_writer import log_xml_metadata
from utils.url_builder import construct_primary_document_url

TARGET_FORMS = {"3", "4", "5", "10-K", "10-Q", "8-K"}
SEC_BASE = "https://www.sec.gov/"

def normalize_url(url: str) -> str:
    return url.strip().replace(SEC_BASE, "")

def backfill_xml_from_exhibits(session: Session, logger=print):
    """Scan exhibit_metadata for XML-based documents and log to xml_metadata."""
    logger("📎 Scanning exhibit_metadata for XML-based exhibits...")

    stmt = (
        select(ExhibitMetadata)
        .join(ParsedSgmlMetadata, ExhibitMetadata.accession_number == ParsedSgmlMetadata.accession_number)
        .join(DailyIndexMetadata, ParsedSgmlMetadata.accession_number == DailyIndexMetadata.accession_number)
        .where(ExhibitMetadata.filename.ilike('%.xml'))
        .where(DailyIndexMetadata.form_type.in_(TARGET_FORMS))
    )

    results = session.execute(stmt).scalars().all()
    logger(f"Found {len(results)} XML exhibits to consider...")

    count_inserted = 0
    for row in results:
        filename = normalize_url(row.filename)

        # Retrieve reliable CIK + form_type
        parsed_sgml = session.get(ParsedSgmlMetadata, row.accession_number)
        cik = parsed_sgml.parent_index.cik

        existing = session.execute(
            select(XmlMetadata).where(
                XmlMetadata.accession_number == row.accession_number,
                XmlMetadata.filename == filename
            )
        ).first()

        if existing:
            continue  # Already logged

        log_xml_metadata({
            "accession_number": row.accession_number,
            "filename": filename,
            "downloaded": False,
            "parsed_successfully": False,
        })

        count_inserted += 1

    logger(f"✅ Backfill complete. {count_inserted} new XML exhibit records inserted.")
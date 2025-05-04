# utils/xml_backfill_utils.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.parsed_sgml_metadata import ParsedSgmlMetadata
from models.xml_metadata import XmlMetadata
from writers.xml_metadata_writer import log_xml_metadata

TARGET_FORMS = {"3", "4", "5", "10-K", "10-Q", "8-K"}
SEC_BASE = "https://www.sec.gov/"

def normalize_url(url: str) -> str:
    return url.strip().replace(SEC_BASE, "")

def backfill_xml_from_primary_doc(session: Session, logger=print):
    """Scan parsed_sgml_metadata for XML primary docs and log to xml_metadata."""
    logger("🔍 Scanning primary_doc_url for XML-based filings...")

    stmt = select(ParsedSgmlMetadata).where(
        ParsedSgmlMetadata.primary_doc_url.ilike('%.xml'),
        ParsedSgmlMetadata.form_type.in_(TARGET_FORMS)
    )

    results = session.execute(stmt).scalars().all()
    logger(f"Found {len(results)} XML primary docs to consider...")

    count_inserted = 0
    for row in results:
        filename = normalize_url(row.primary_doc_url)
        url = row.primary_doc_url.strip()

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
            "cik": row.cik,
            "form_type": row.form_type,
            "filename": filename,
            "url": url,
            "downloaded": False,
            "parsed_successfully": False,
            "source": "primary_doc",
            "content_type": "xml"
        })

        count_inserted += 1

    logger(f"✅ Backfill complete. {count_inserted} new XML records inserted.")

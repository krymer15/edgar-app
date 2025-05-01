# ORM Ingestion Base Runner --- /scripts/ingest_submissions.py
# Parses JSON, writes into CompaniesMetadata and SubmissionsMetadata using SQLAlchemy ORM

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from utils.get_project_root import get_project_root
from utils.config_loader import ConfigLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.companies import CompaniesMetadata
from models.submissions import SubmissionsMetadata
from datetime import datetime

config = ConfigLoader.load_config()
DATABASE_URL = config["database"]["url"]

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
print(f"Connecting to database at: {DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        # ISO 8601 format from filings.recent
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # Fallback for compact SEC format
            return datetime.strptime(dt_str, "%Y%m%d%H%M%S")
        except ValueError:
            return None

def parse_items(raw_items):
    if raw_items is None:
        return None
    if isinstance(raw_items, list):
        return raw_items
    if isinstance(raw_items, str):
        return [item.strip() for item in raw_items.split(",")]
    return None

def ingest_submissions_from_folder(folder_path: str):
    """Ingest all JSON files inside a given folder into the database."""
    session = SessionLocal()

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                filepath = os.path.join(folder_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                print(f"\n🔹 Processing file: {filename}")
                print(f"Company CIK: {data.get('cik')}")
                print(f"Company Name: {data.get('name')}")

                filings_recent = data.get("filings", {}).get("recent", {})
                accession_numbers = filings_recent.get("accessionNumber", [])

                print(f"Submissions keys found: {list(filings_recent.keys())}")
                print(f"Number of filings found: {len(accession_numbers)}")

                # Insert or update company metadata
                company = CompaniesMetadata(
                    cik=data.get("cik"),
                    entity_type=data.get("entityType"),
                    sic=data.get("sic"),
                    sic_description=data.get("sicDescription"),
                    name=data.get("name"),
                    tickers=data.get("tickers"),
                    exchanges=data.get("exchanges"),
                    ein=data.get("ein"),
                    description=data.get("description"),
                    website=data.get("website"),
                    investor_website=data.get("investorWebsite"),
                    category=data.get("category"),
                    fiscal_year_end=data.get("fiscalYearEnd"),
                    state_of_incorporation=data.get("stateOfIncorporation"),
                    state_of_incorporation_description=data.get("stateOfIncorporationDescription"),
                    mailing_address=data.get("addresses", {}).get("mailing"),
                    business_address=data.get("addresses", {}).get("business"),
                    phone=data.get("phone"),
                )
                session.merge(company)  # Safe upsert

                # Insert filings
                for idx, accession_number in enumerate(accession_numbers):
                    filing = SubmissionsMetadata(
                        accession_number=accession_number,
                        cik=data.get("cik"),
                        filing_date=filings_recent.get("filingDate", [None])[idx],
                        report_date=filings_recent.get("reportDate", [None])[idx] or None,
                        form_type=filings_recent.get("form", [None])[idx],
                        items=parse_items(filings_recent.get("items", [None])[idx]),
                        primary_document=filings_recent.get("primaryDocument", [None])[idx],
                        document_description=filings_recent.get("primaryDocDescription", [None])[idx] or None,
                        is_xbrl=filings_recent.get("isXBRL", [False])[idx],
                        is_inline_xbrl=filings_recent.get("isInlineXBRL", [False])[idx],
                        acceptance_datetime=parse_datetime(filings_recent.get("acceptanceDateTime", [None])[idx]),
                    )
                    session.merge(filing)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    # Build the full path dynamically from project root
    folder = os.path.join(get_project_root(), "data/raw/submissions/")
    ingest_submissions_from_folder(folder)

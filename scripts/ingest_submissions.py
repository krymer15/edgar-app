import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.companies import CompaniesMetadata
from models.submissions import SubmissionsMetadata
from datetime import datetime

# Database connection string from your .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/myagentdb")

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_datetime(dt_str):
    """Parse SEC's acceptanceDateTime (format yyyymmddhhmmss) into datetime."""
    if not dt_str:
        return None
    return datetime.strptime(dt_str, "%Y%m%d%H%M%S")

def ingest_submissions_from_folder(folder_path: str):
    """Ingest all JSON files inside a given folder into the database."""
    session = SessionLocal()

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                filepath = os.path.join(folder_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

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

                # Insert submissions (recent filings)
                submissions = data.get("submissions", {}).get("recent", {})
                for idx in range(len(submissions.get("accessionNumber", []))):
                    filing = SubmissionsMetadata(
                        accession_number=submissions["accessionNumber"][idx],
                        cik=data.get("cik"),
                        filing_date=submissions.get("filingDate", [None])[idx],
                        report_date=submissions.get("reportDate", [None])[idx],
                        form_type=submissions.get("form", [None])[idx],
                        items=submissions.get("items", [None])[idx],
                        primary_document=submissions.get("primaryDocument", [None])[idx],
                        document_description=submissions.get("primaryDocDescription", [None])[idx],
                        is_xbrl=submissions.get("isXBRL", [False])[idx],
                        is_inline_xbrl=submissions.get("isInlineXBRL", [False])[idx],
                        acceptance_datetime=parse_datetime(submissions.get("acceptanceDateTime", [None])[idx]),
                    )
                    session.merge(filing)  # Safe upsert

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    folder = "C:\Users\Kris Acer PC\Dropbox\Safe Harbor\AI Projects\edgar-app\"
    ingest_submissions_from_folder(folder)

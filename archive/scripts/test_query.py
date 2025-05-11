import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.submissions import SubmissionsMetadata
import os

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment or config.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def query_filings_by_cik(cik: str):
    """Query and print filings for a given CIK."""
    session = SessionLocal()
    try:
        filings = session.query(SubmissionsMetadata).filter(SubmissionsMetadata.cik == cik).all()
        for filing in filings:
            print(f"Accession: {filing.accession_number} | Form: {filing.form_type} | Filed: {filing.filing_date}")
    finally:
        session.close()

session = SessionLocal()
total = session.query(SubmissionsMetadata).count()
print(f"Total filings in database: {total}")
session.close()

if __name__ == "__main__":
    # Example CIK you loaded (Apple)
    cik_to_query = "0000320193"
    query_filings_by_cik(cik_to_query)

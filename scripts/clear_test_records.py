# scripts/clear_test_records.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from sqlalchemy import delete
from utils.database import SessionLocal
from models.parsed_sgml_metadata import ParsedSgmlMetadata
from models.exhibit_metadata import ExhibitMetadata


def clear_records(filing_date=None, run_id=None):
    session = SessionLocal()
    try:
        if not filing_date and not run_id:
            raise ValueError("You must provide at least a --date or --run_id")

        # Step 1: Find accession numbers to delete
        query = session.query(ParsedSgmlMetadata.accession_number)

        if filing_date:
            query = query.filter(ParsedSgmlMetadata.filing_date == filing_date)

        if run_id:
            query = query.filter(ParsedSgmlMetadata.run_id == run_id)

        accession_numbers = [row.accession_number for row in query.all()]

        if not accession_numbers:
            print("No matching records found. Nothing to delete.")
            return

        print(f"Found {len(accession_numbers)} filings to delete.")

        # Step 2: Delete exhibits
        session.execute(
            delete(ExhibitMetadata).where(
                ExhibitMetadata.accession_number.in_(accession_numbers)
            )
        )

        # Step 3: Delete parsed metadata
        session.execute(
            delete(ParsedSgmlMetadata).where(
                ParsedSgmlMetadata.accession_number.in_(accession_numbers)
            )
        )

        session.commit()
        print("Records deleted successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error during deletion: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete test filings by date or run ID.")
    parser.add_argument("--date", type=str, help="Filing date to delete (YYYY-MM-DD)")
    parser.add_argument("--run_id", type=str, help="Run ID to delete (optional)")
    args = parser.parse_args()

    clear_records(filing_date=args.date, run_id=args.run_id)

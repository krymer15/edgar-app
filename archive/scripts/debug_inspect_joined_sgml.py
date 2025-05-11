import os, sys

'''
 Self-contained debug test CLI runner to confirm that your ParsedSgmlMetadata → DailyIndexMetadata join works correctly and returns `form_type`, `cik`, and `primary_doc_url`.
'''

# Ensure project root is in path
try:
    from utils.get_project_root import get_project_root
    sys.path.insert(0, str(get_project_root()))
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.database import SessionLocal
from sqlalchemy import select
from models.parsed_sgml_metadata import ParsedSgmlMetadata
from models.daily_index_metadata import DailyIndexMetadata

def main():
    session = SessionLocal()
    try:
        print("🔎 Inspecting joined ParsedSgmlMetadata → DailyIndexMetadata")

        stmt = (
            select(ParsedSgmlMetadata)
            .join(ParsedSgmlMetadata.parent_index)
            .where(DailyIndexMetadata.form_type.in_(["3", "4", "5"]))
            .limit(5)
        )
        results = session.execute(stmt).scalars().all()

        for row in results:
            print("—" * 60)
            print(f"Accession Number:  {row.accession_number}")
            print(f"CIK:               {row.parent_index.cik}")
            print(f"Form Type:         {row.parent_index.form_type}")
            print(f"Primary Doc URL:   {row.primary_doc_url}")
        if not results:
            print("⚠️ No results found. Check if SGML metadata is ingested.")

    finally:
        session.close()
        print("✅ Session closed.")

if __name__ == "__main__":
    main()

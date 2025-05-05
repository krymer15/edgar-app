# scripts/backfill_xml_exhibits.py

import os, sys

# Ensure root is in sys.path
try:
    from utils.get_project_root import get_project_root
    sys.path.insert(0, str(get_project_root()))
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.database import SessionLocal
from utils.xml_backfill_utils import backfill_xml_from_exhibits

def main():
    print("🚀 Starting XML backfill from exhibits only...")
    session = SessionLocal()
    try:
        backfill_xml_from_exhibits(session)
    finally:
        session.close()
        print("🏁 Backfill completed and DB session closed.")

if __name__ == "__main__":
    main()

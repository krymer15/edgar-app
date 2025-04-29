# ORM-based table creation ... /scripts/init_db.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.get_project_root import get_project_root
from dotenv import load_dotenv
from sqlalchemy import create_engine
from models.base import Base
from models.companies import CompaniesMetadata
from models.submissions import SubmissionsMetadata

# Load .env explicitly using full path
dotenv_path = os.path.join(get_project_root(), ".env")
load_dotenv(dotenv_path)

# Database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/edgar_app_db")

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)
print(f"Connecting to database at: {DATABASE_URL}")
print(f"Resolved dotenv path: {dotenv_path}")


def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("✅ Tables created successfully.")

# scripts/init_db.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config_loader import ConfigLoader
from sqlalchemy import create_engine
from models.base import Base

# Explicit model imports to register with Base metadata
from models.companies import CompaniesMetadata
from models.submissions import SubmissionsMetadata
from models.daily_index_metadata import DailyIndexMetadata

def create_tables():
    config = ConfigLoader.load_config()
    db_url = config["database"]["url"]

    engine = create_engine(db_url)
    print(f"🔗 Connecting to database at: {db_url}")
    
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    create_tables()

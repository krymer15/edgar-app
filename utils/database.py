# /utils/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from utils.config_loader import ConfigLoader

# Load environment variables from .env
load_dotenv()

# Load app config
_config_loader = ConfigLoader()
config = _config_loader.load_config()

# Prefer config["database.url"], fallback to os.environ["DATABASE_URL"]
DATABASE_URL = config.get("database", {}).get("url") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in app_config.yaml or .env")

print(f"🔌 Loaded DATABASE_URL: {DATABASE_URL}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Helper function for consistent session access
def get_db_session():
    return SessionLocal()

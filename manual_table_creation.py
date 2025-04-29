from sqlalchemy import create_engine
from models.base import Base
from models.daily_index_metadata import DailyIndexMetadata

# Load your DATABASE_URL
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/edgar_app_db"

engine = create_engine(DATABASE_URL)

# This will create any missing tables
Base.metadata.create_all(engine)

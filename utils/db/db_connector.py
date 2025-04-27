# utils/db/db_connector.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class PostgresConnector:

    '''
    ***USE FROM ANYWHERE***
    
    from utils.db.db_connector import PostgresConnector

    db = PostgresConnector()

    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            print(result)
    '''

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment variables.")

    def connect(self):
        """
        Creates and returns a new database connection.
        Usage: with PostgresConnector().connect() as conn:
        """
        return psycopg2.connect(self.db_url)

import psycopg2
import os
from utils.config_loader import ConfigLoader
from psycopg2.extras import execute_values

class DailyIndexWriter:
    def __init__(self):
        config = ConfigLoader.load_config()
        self.db_url = config["postgres"]["DATABASE_URL"]  # pulled from app_config.yaml

    def write_to_postgres(self, filings: list):
        if not filings:
            print("⚠️ No filings to write.")
            return

        print(f"📥 Inserting {len(filings)} filings into daily_index_metadata...")

        insert_query = """
        INSERT INTO daily_index_metadata (
            accession_number, cik, form_type, filing_date, filing_url
        ) VALUES %s
        ON CONFLICT (accession_number) DO NOTHING;
        """

        values = [
            (
                f["accession_number"],
                f["cik"],
                f.get("form_type"),
                f.get("filing_date"),
                f["filing_url"]
            )
            for f in filings
        ]

        try:
            conn = psycopg2.connect(self.db_url)
            with conn:
                with conn.cursor() as cur:
                    execute_values(cur, insert_query, values)
            print(f"✅ Inserted {len(values)} rows into daily_index_metadata")
        except Exception as e:
            print(f"[ERROR] Failed DB insert: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

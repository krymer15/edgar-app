# agent_plugins/vector_store.py

import os
import psycopg2
from psycopg2.extras import register_uuid
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
register_uuid()

# Connect once (use connection pooling for production later)
PGVECTOR_CONN_STRING = os.getenv("PGVECTOR_DB_URL")
client = OpenAI()


def connect():
    return psycopg2.connect(PGVECTOR_CONN_STRING)


def create_summary_table():
    """
    Creates the pgvector table if it doesn't exist.
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;

                CREATE TABLE IF NOT EXISTS filing_summaries (
                    id SERIAL PRIMARY KEY,
                    ticker TEXT,
                    company TEXT,
                    filing_date DATE,
                    accession TEXT UNIQUE,
                    summary TEXT,
                    embedding vector(1536)
                );
            """)
            conn.commit()
        print("✅ Table 'filing_summaries' ready.")


def embed_text(text: str) -> list[float]:
    """
    Use OpenAI to embed the summary.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text.strip()]
    )
    return response.data[0].embedding


def store_summary_vector(filing, summary: str):
    """
    Embeds and stores the summary + filing metadata in Postgres.
    """
    try:
        embedding = embed_text(summary)

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO filing_summaries (
                        ticker, company, filing_date, accession, summary, embedding, raw_text
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (accession) DO NOTHING;
                """, (
                    getattr(filing, 'ticker', 'UNKNOWN'),
                    getattr(filing, 'company', 'Unknown Company'),
                    getattr(filing, 'filing_date', None),
                    getattr(filing, 'accession_no', None),
                    summary,
                    embedding,
                    getattr(filing, 'raw_text', None)  # ✅ This must be passed in
                ))
                conn.commit()
                print("✅ Summary vector stored.")
    except Exception as e:
        print(f"❌ Failed to store vector: {e}")

def store_exhibit_vector(filing, label: str, summary: str, exhibit_text: str = None):
    """
    Stores a summarized exhibit in the exhibit_summaries table with a foreign key to the filing.
    """
    try:
        embedding = embed_text(summary)
        accession = getattr(filing, 'accession_no', None)

        with connect() as conn:
            with conn.cursor() as cur:
                # Ensure table and foreign key exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS exhibit_summaries (
                        id SERIAL PRIMARY KEY,
                        ticker TEXT,
                        company TEXT,
                        filing_date DATE,
                        accession TEXT,
                        exhibit_label TEXT,
                        summary TEXT,
                        embedding vector(1536),
                        filing_id INTEGER,
                        UNIQUE (accession, exhibit_label)
                    );
                """)

                # Lookup filing ID
                cur.execute("SELECT id FROM filing_summaries WHERE accession = %s;", (accession,))
                filing_row = cur.fetchone()
                filing_id = filing_row[0] if filing_row else None

                # Insert
                cur.execute("""
                    INSERT INTO exhibit_summaries (
                        ticker, company, filing_date, accession, exhibit_label,
                        summary, embedding, filing_id, exhibit_text
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (accession, exhibit_label) DO NOTHING;
                """, (
                    getattr(filing, 'ticker', 'UNKNOWN'),
                    getattr(filing, 'company', 'Unknown Company'),
                    getattr(filing, 'filing_date', None),
                    accession,
                    label,
                    summary,
                    embedding,
                    filing_id,
                    exhibit_text # ✅ store full exhibit text
                ))

                conn.commit()
                print(f"✅ Stored exhibit: {label}")
    except Exception as e:
        print(f"❌ Failed to store exhibit vector: {e}")



def search_similar_summaries(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Searches for similar summaries using cosine distance.
    """
    try:
        embedding = embed_text(query_text)
        embedding_str = f"[{', '.join(str(x) for x in embedding)}]"

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        ticker,
                        company,
                        filing_date,
                        accession,
                        summary,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM filing_summaries
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """, (embedding_str, embedding_str, top_k))

                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "ticker": row[0],
                        "company": row[1],
                        "filing_date": row[2],
                        "accession": row[3],
                        "summary": row[4],
                        "similarity": float(row[5])
                    })
                return results

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []


def list_all_summaries(limit: int = 10) -> list[dict]:
    """
    Returns recent stored summaries with basic metadata.
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ticker, company, filing_date, accession, LEFT(summary, 300)
                    FROM filing_summaries
                    ORDER BY filing_date DESC
                    LIMIT %s;
                """, (limit,))
                return cur.fetchall()
    except Exception as e:
        print(f"❌ Failed to list summaries: {e}")
        return []

def list_all_exhibits(limit: int = 10) -> list[dict]:
    """
    Returns recent stored exhibit summaries with metadata.
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ticker, company, filing_date, accession, exhibit_label, LEFT(summary, 300)
                    FROM exhibit_summaries
                    ORDER BY filing_date DESC
                    LIMIT %s;
                """, (limit,))
                rows = cur.fetchall()
                return [
                    {
                        "ticker": row[0],
                        "company": row[1],
                        "filing_date": row[2],
                        "accession": row[3],
                        "exhibit_label": row[4],
                        "summary_preview": row[5]
                    } for row in rows
                ]
    except Exception as e:
        print(f"❌ Failed to list exhibit summaries: {e}")
        return []

# Safe Harbor EDGAR AI Platform

A modular, scalable platform for SEC EDGAR filings ingestion, AI-driven parsing, and future vector search integration.

---

## 🏗️ Project Structure

```bash
edgar-app/
├── config/              # Centralized app configuration (YAML)
├── downloaders/         # SEC API and raw HTML downloaders
├── parsers/             # Exhibit and filing parsers
├── utils/               # Utility functions and loaders
│   └── db/              # Database connectors and vector store utilities
├── scripts/             # Orchestration scripts (process filings)
├── data/                # Raw and processed filing storage
├── infra/               # Infrastructure (e.g., Docker Compose for Postgres + pgvector)
├── notebooks/           # Jupyter notebooks for development
├── tests/               # Unit tests
├── output/              # Output artifacts (temporary working files)
├── .env                 # Environment variables
├── requirements.txt     # Production Python dependencies
├── README.md            # (This file)
└── tree_view.py         # Tree visualization utility
```

## Architectural Distinctions

| Function                | Output Type             | Storage Target                    |
| ----------------------- | ----------------------- | --------------------------------- |
| Downloader              | Raw `.xml` or `.html`   | `/data/raw/...` (filesystem only) |
| Parser                  | Structured dict         | In-memory return only             |
| Writer (DB)             | Parsed metadata         | PostgreSQL (via SQLAlchemy)       |
| Writer (File, optional) | Cleaned XML/text/parsed | `/data/processed/...`             |
| Orchestrator            | Invokes all above       | N/A – coordinates flow            |

---

🚀 Features
SEC Filings Ingestion: 8-K, 10-K, S-1, 13D, 13G forms supported.

Exhibit Parsing: Clean text block extraction from HTML filings.

AI Summarization Ready: OpenAI API integration prepared.

Vector Embedding Ready: PostgreSQL + pgvector support for RAG workflows.

Centralized Configuration: Managed via /config/app_config.yaml.

Production Infrastructure: Local Postgres and vector store via Docker Compose.

Strict Modularity: Single-responsibility classes, config-driven architecture.

⚙️ Setup Instructions
1. Clone the repository
```bash
git clone https://github.com/yourusername/edgar-app.git
cd edgar-app
```
2. Create and activate environment
```bash
python -m venv edgar-env
.\edgar-env\Scripts\activate   # Windows
```
# OR
```bash
source edgar-env/bin/activate  # macOS/Linux
```
3. Install required packages
```bash
pip install -r requirements.txt
```
4. Set up environment variables
Copy .env.example or create .env

Fill in required fields (OpenAI Key, Postgres credentials, etc.)

Example .env:
```python
OPENAI_API_KEY=your-openai-key
POSTGRES_DB=yourdbname
POSTGRES_USER=youruser
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://user:password@localhost:5432/yourdbname
```
5. (Optional) Start local Postgres + pgvector using Docker
```bash
cd infra
docker-compose up -d
```
🛠️ How to Run Filing Ingestion
Process filings for a single company:
```bash
python scripts/process_company_filings.py
```

Maps Ticker → CIK (TickerCIKMapper)

Downloads latest filings (SECDownloader)

Saves raw HTML and metadata (FileSaver)

Parses exhibit text blocks (ExhibitParser)

Saves parsed blocks for downstream analysis

🧠 Core Technologies
Python 3.11+

PostgreSQL + pgvector

OpenAI API (text embedding, future summarization)

BeautifulSoup4, lxml (HTML parsing)

Docker Compose (infrastructure orchestration)

📦 Future Roadmap
 Live filing monitors with RSS + Daily Index backfill

 Filing summarization using LLMs

 Vector search across 8-K, 10-K exhibits

 Lightweight Retrieval-Augmented Generation (RAG) system

 Async ingestion and search

🧹 Maintenance Scripts
`clear_pycache.bat`: Clear all compiled Python caches.

`docker-compose.yml` (inside `/infra/`): Run Postgres + pgvector locally.

📣 Notes
This project strictly enforces modularity, config-driven development, and separation of concerns to maintain scalability and reliability across ingestion and analysis pipelines.

### Recommended Best Practices for financial ingestion pipelines:
✅ RECOMMENDED BEST PRACTICES
For Financial/Regulatory Ingestion Pipelines

1. Minimal Redundancy, Strong Referential Integrity
Use foreign keys to tie all ingestion metadata (SGML, XML, Exhibits) to accession_number

Avoid storing CIK, form_type, or filing_date in multiple tables unless needed for indexing or lookup speed

2. Canonical URL or Filename Deduplication
Deduplicate on: accession_number + filename or accession_number + url

Ensure xml_metadata has UNIQUE (accession_number, filename) ✅ already done

Normalize URLs to lowercase and strip https://www.sec.gov/Archives/ to avoid variations

3. Source Transparency (Traceability)
Track source = embedded, primary_doc, or exhibit to preserve how/where the XML was found

This allows downstream analysis of ingestion coverage and data lineage

4. Merge vs Insert Logic
Always merge records where duplicates may exist across discovery methods

Never allow silent overwrites of critical fields (parsed_successfully should only be upgraded to True)

5. Time-Based Logging
Timestamps (created_at, updated_at) help track data freshness

Optional: Add parse_attempts, last_attempt_at if retry logic is built later

## Phase 2B: XML Ingestion + Metadata Logging

- Tracks Form 4, 3, 5, and 10-K XML files via `xml_metadata` table
- Deduplicates based on accession_number + filename
- Discovery sources:
  - `parsed_sgml_metadata.primary_doc_url` (normalized)
  - Future: `exhibit_metadata` for .xml exhibits
- Utilities:
  - `utils/xml_backfill_utils.py` = discovery logic
  - `scripts/backfill_xml_primary.py` = CLI runner
  - `log_xml_metadata()` = safe insert/update with fallback

Run:
```bash
python scripts/backfill_xml_primary.py
```


# Safe Harbor EDGAR AI Platform

A modular, scalable platform for SEC EDGAR filings ingestion, AI-driven parsing, and future vector search integration.

---

## 🏗️ Project Structure

```text
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
```
git clone https://github.com/yourusername/edgar-app.git
cd edgar-app
```
2. Create and activate environment
```
python -m venv edgar-env
.\edgar-env\Scripts\activate   # Windows
```
# OR
```
source edgar-env/bin/activate  # macOS/Linux
```
3. Install required packages
```
pip install -r requirements.txt
```
4. Set up environment variables
Copy .env.example or create .env

Fill in required fields (OpenAI Key, Postgres credentials, etc.)

Example .env:
```
OPENAI_API_KEY=your-openai-key
POSTGRES_DB=yourdbname
POSTGRES_USER=youruser
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://user:password@localhost:5432/yourdbname
```
5. (Optional) Start local Postgres + pgvector using Docker
```
cd infra
docker-compose up -d
```
🛠️ How to Run Filing Ingestion
Process filings for a single company:
```
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
clear_pycache.bat: Clear all compiled Python caches.

docker-compose.yml (inside /infra/): Run Postgres + pgvector locally.

📣 Notes
This project strictly enforces modularity, config-driven development, and separation of concerns to maintain scalability and reliability across ingestion and analysis pipelines.
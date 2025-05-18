# Safe Harbor EDGAR AI Platform

This repository powers the Safe Harbor EDGAR AI platform, an in-house system for ingesting, parsing, vectorizing, and AI-summarizing SEC EDGAR filings. It's built around modular pipelines and clear data models.

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- Docker (optional, for containerized database)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd edgar-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your database:**
   - Using Docker:
     ```bash
     docker-compose up -d
     ```
   - Or connect to an existing PostgreSQL instance by setting `DATABASE_URL` in your `.env` file

4. **Create data directories:**
   ```bash
   # For production data (can point to an external drive)
   ln -s /path/to/external/storage/edgar_data data

   # For test data 
   ln -s /path/to/test/data test_data
   ```

## Project Architecture

The system is organized into several key modules:

### Core Ingestion Components

- **collectors/** - Fetch data from SEC sources (daily index, submissions API)
- **downloaders/** - Download raw filing documents and handle caching
- **parsers/** - Transform raw documents into structured objects
  - Contains document-type subfolders (sgml, html, xbrl)
  - Each subfolder may contain specialized components:
    - **indexers/** - Extract document metadata and content blocks
    - **cleaners/** - Normalize and sanitize raw content
- **writers/** - Persist parsed data to the database
- **orchestrators/** - Coordinate the components into complete pipelines
- **models/** - Data models for both in-memory processing and database persistence
- **utils/** - Shared utilities for paths, logging, configuration, etc.

### Pipeline Architecture

The system implements three main pipelines for SEC data:

1. **Pipeline 1** - Filing metadata from crawler.idx
2. **Pipeline 2** - Document metadata extraction from SGML
3. **Pipeline 3** - SGML file download and storage to disk

These pipelines can be run independently or coordinated through the `DailyIngestionPipeline` meta-orchestrator.

### Key Architectural Principles

The project is structured around several architectural principles:

#### 1. Separation of Concerns
Each component type has a specific responsibility in the data flow:
- **Collectors**: Fetch metadata and raw files from external sources
- **Downloaders**: Handle HTTP requests and file downloading
- **Parsers**: Transform raw data into structured formats
  - **Indexers**: Extract document blocks from container files (e.g., SGML)
  - **Cleaners**: Normalize and sanitize raw document content
  - **Format-specific parsers**: Extract structured data from specific document formats
- **Writers**: Persist structured data to the database
- **Orchestrators**: Coordinate the end-to-end processing flow

#### 2. Data Flow Architecture
The data flows through the system in a clear direction:
```
                           ┌── Indexers ─┐
                           │             │
Raw Data → Collectors → Downloaders → Parsers → Writers → Database
                           │             │
                           └── Orchestrators
```

A more detailed document processing flow:
```
Raw Container File (SGML/IDX)
      ↓
Indexer → Extract document blocks/pointers
      ↓
Document Selector → Select primary document
      ↓
Format-Specific Parser → Process specific document format
      ↓
Form-Specific Parser → Extract form-specific data
      ↓
Structured Data Output → Ready for database writers
```

#### 3. Data Model Separation
- **Dataclasses**: Pure Python dataclasses for in-memory processing
- **ORM Models**: SQLAlchemy models for database operations
- **Adapters**: Convert between dataclasses and ORM models

#### 4. Form Type Specialization
Form-specific logic is isolated in dedicated modules:
- Form-specific parsers in `parsers/forms/`
- Form-specific writers in `writers/forms/`
- Form-specific orchestrators in `orchestrators/forms/`

## Running the Application

### Core Scripts

```bash
# Run the full pipeline (all three pipelines in sequence)
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12

# Run only the metadata ingestion (Pipeline 1)
python -m scripts.crawler_idx.run_daily_metadata_ingest --date 2025-05-12

# Run specialized form processing
python -m scripts.forms.run_form4_ingest --date 2025-05-12
```

### Filtering Options

Most scripts support form type filtering:

```bash
# Process only 10-K and 8-K filings
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --include-forms 10-K 8-K
```

### Backfilling Historical Data

```bash
# Backfill the last 7 days of filing data
python -m scripts.crawler_idx.run_daily_metadata_ingest --backfill 7
```

## Data Directory Structure

The `data/` directory is a symlink that points to an external storage location. This approach:

1. Keeps large data files out of Git
2. Enables mounting external drives or network storage
3. Allows different developers to use different storage locations

### Data Storage Configuration

The data storage paths are configured in `config/app_config.yaml`:

```yaml
storage:
  # Base path for all data storage
  base_data_path: "./data/"
  
  # Specific paths for different data types
  raw_html_base_path: "data/raw/"
  cleaned_base_path: "data/cleaned/"
  parsed_base_path: "data/parsed/"
```

## Testing

Run tests using pytest:

```bash
pytest tests/shared/  # Run shared utility tests
pytest tests/crawler_idx/  # Run crawler.idx pipeline tests
pytest  # Run all tests
```

When running tests, the system automatically uses `./test_data/` instead of the production data directory.

## Database Schema

The system uses PostgreSQL with the following core tables:

- **filing_metadata** - Basic information about SEC filings
- **filing_documents** - Document blocks extracted from SGML submissions
- **form4_filings** - Form 4 filing-specific data
- **form4_transactions** - Individual transactions from Form 4 filings
- **companies_metadata** - Company information from Submissions API
- **submissions_metadata** - Filing data from Submissions API

## Docker Support

The project includes Docker support for the database:

```yaml
# docker-compose.yml
services:
  postgres:
    image: ankane/pgvector
    container_name: ai_agent_postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: myagentdb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - D:/safeharbor-postgres/data:/var/lib/postgresql/data
```

## Project Standards

- **Testing**: Use pytest for all tests
- **Documentation**: Each module has a README.md explaining its role
- **Dataclasses**: Use Python's `@dataclass` containers for data exchange
- **Logging**: Use `utils.report_logger` for consistent logging
- **Configuration**: Use `config.config_loader` for app-wide settings

## Additional Documentation

- **SEC Forms**: Documentation on SEC form types in `docs/sec_forms.md`
- **Module READMEs**: Each module directory contains a detailed README.md
- **Code Documentation**: Docstrings document class and function usage
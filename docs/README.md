# Safe Harbor EDGAR AI Platform

A modular, GPT-integrated platform for parsing, summarizing, and storing SEC EDGAR filings.

## ✅ Core Features

- Batch ingestion from `crawler.idx` using SGML `.txt` filings
- Exhibit extraction and tagging
- Primary document URL resolution
- Postgres + SQLAlchemy ORM metadata storage
- Ingestion logs to CSV
- Canonical field enforcement (`primary_doc_url`, not `primary_document_url`)

## 🧱 Architecture

| Layer       | Modules                              |
|------------|---------------------------------------|
| Ingestion  | `daily_index_collector.py`, `batch_sgml_ingestion_orchestrator.py` |
| Parsing    | `sgml_filing_parser.py`, `index_page_parser.py` |
| Writing    | `parsed_sgml_writer.py`, `report_logger.py` |
| Utilities  | `field_mapper.py`, `path_manager.py`, `config_loader.py` |
| Schema     | `parsed_result_model.py`, `*_metadata.py` |

## 🧪 Tests

Run with `pytest` or `unittest` inside `/tests/`:

- Metadata writer tests
- Path builder logic
- Ingestion log file creation

## 🧠 Future Phases

- GPT-powered `exhibit_summary_writer.py`
- Real-time `filing_monitor.py`
- Digest generator and dashboard

## 🚀 Getting Started

1. Set up your `.env` and `app_config.yaml`
2. Start Postgres: `docker-compose up -d`
3. Run batch ingestion:
```bash
python ingest_sgml_batch_from_idx.py --date 2025-05-03

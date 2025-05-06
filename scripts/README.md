# 🛠️ Developer CLI Runners

This folder contains standalone developer tools for testing, backfilling, or manually triggering ingestion pipelines within the Safe Harbor EDGAR AI Platform.

These scripts are **not used in production** — they are intended for internal development, debugging, and custom backfills.

---

## 📄 `run_form4_xml_ingest.py`

Run a full ingestion cycle for a single Form 4 XML file. This includes:

- Downloading the specified `.xml` file from the SEC
- Parsing the XML using `Form4Parser`
- Writing parsed data to Postgres using `Form4Writer`

### ✅ Example

```bash
python scripts/run_form4_xml_ingest.py \
  --cik 921895 \
  --accession 0000921895-25-001190 \
  --filename xslF345X05_primary.xml \
  --date 2025-04-28
```

### 🔧 How It Works
- Loads project settings via .env and app_config.yaml
- Inserts project root dynamically for safe imports
- Uses SQLAlchemy session from utils/database.py
- Uses Form4XmlOrchestrator to coordinate download → parse → write

### Notes
Notes
- Scripts are modular and orchestrator-driven.
- Global CIK/form_type filtering is supported via `FilteredCikManager`.
- Use `--skip_filter` in `ingest_sgml_batch_from_idx.py` to ingest all filings without filtering.
- To avoid duplication, all writers use `merge()` for safe upserts in Postgres.
- All downloaded XML files are saved under `/data/raw/{year}/{cik}/{form_type}/{accession}/filename.xml`
- Only the file named via --filename is downloaded (not all XMLs under the accession)
- Output is written to the form4_filings table in Postgres
- This script is useful for spot-checking filings or prototyping parser changes

### Folder Summary

| Script                               | Purpose                                                                 | Orchestrator(s) Used                                               | Populates `daily_index_metadata`? | Parses SGML?       |
|--------------------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------|-----------------------------------|--------------------|
| `ingest_daily_index.py`              | **Metadata-only ingestion** from `crawler.idx`                          | ✅ `DailyIndexOrchestrator`                                        | ✅ Yes                             | ❌ No               |
| `ingest_from_source.py`              | Unified CLI for `daily_index` or `submissions_api` sources              | ✅ `DailyIndexOrchestrator` or `SubmissionsIngestionOrchestrator` | ✅ Yes (for daily\_index)          | ❌ No               |
| `ingest_sgml_batch_from_idx.py`      | **Filtered SGML ingestion + optional metadata write**                   | ✅ `BatchSgmlIngestionOrchestrator`                                | ✅ If filtering is enabled         | ✅ Yes              |
| `run_form4_xml_ingest.py`           | Ingest and parse a **single Form 4 XML** from SEC                       | ✅ `Form4XmlOrchestrator`                                          | ❌                                 | ✅ Yes (XML only)   |

- UPDATE needed for above table. `ingest_daily_index.py` has been deprecated and replaced by `ingest_sgml_batch_from_idx.py`, which is the single source for filtered SGML parsing and `daily_index_metadata`.
- `ingest_from_source.py` should only be used for the Submissions API pipeline.
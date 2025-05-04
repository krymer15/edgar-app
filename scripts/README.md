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
- All downloaded XML files are saved under /data/raw/{year}/{cik}/{form_type}/{accession}/filename.xml

- Only the file named via --filename is downloaded (not all XMLs under the accession)

- Output is written to the form4_filings table in Postgres

- This script is useful for spot-checking filings or prototyping parser changes

### Folder Summary

| Script Name                     | Purpose                                     |
| ------------------------------- | ------------------------------------------- |
| `run_form4_xml_ingest.py`       | Ingest a specific Form 4 XML file           |
| `ingest_sgml_batch_from_idx.py` | Batch ingest of all SGML filings for a date |

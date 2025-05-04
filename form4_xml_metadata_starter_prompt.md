# 🧠 PROJECT CONTEXT  
I’m building an AI-powered SEC filing ingestion platform. I’ve completed:

- SGML pipeline for 8-Ks using `daily_index_metadata` + `parsed_sgml_metadata`
- Exhibit logging via `exhibit_metadata` table
- Form 4 XML pipeline using `form4_xml_orchestrator`, `Form4XmlDownloader`, `Form4Parser`, and `Form4Writer`
- File paths and metadata follow the `/data/raw/{year}/{cik}/{form_type}/{accession}/{filename}.xml` structure
- All ingestion runs log to `ingestion_report_YYYY-MM-DD.csv`

---

## 🎯 GOAL OF THIS THREAD  
Design a clean and extensible metadata schema for **Form 4 XML files**, and determine:

1. Should `exhibit_metadata` be reused or extended?
2. Should a new `xml_metadata` table be created for Form 4 `.xml` tracking?
3. How can this be integrated with existing SGML-derived form metadata to unify daily ingestion tracking?

---

## 📁 MODULES ALREADY BUILT  
You can refer to or ask me to upload any of the following if helpful:

| File / Module                     | Purpose                                      |
|----------------------------------|----------------------------------------------|
| `form4_xml_orchestrator.py`      | Orchestrates download → parse → write        |
| `form4_xml_downloader.py`        | Downloads only selected `.xml` files         |
| `form4_parser.py`                | Extracts structured fields from XML          |
| `form4_writer.py`                | Writes parsed result to `form4_filings`      |
| `exhibit_metadata` table         | Logs exhibit filename, type, accessible flag |
| `daily_index_writer.py`          | Writes filing metadata to `daily_index_metadata` from SGML |
| `app_config.yaml`                | Contains `base_data_path` + path template    |
| `scripts/run_form4_xml_ingest.py`| CLI dev runner for targeted XML ingestion    |

---

## 💾 EXISTING TABLES  
- `exhibit_metadata`: logs filenames, exhibit types, download status
- `form4_filings`: main parsed content (ownership, transaction, etc.)
- `daily_index_metadata`: form-level metadata from `crawler.idx`

---

## 📦 IDEAL OUTCOME  
- Centralized metadata source across all pipelines
- Can support both downloaded and “discovered but skipped” files
- Enables backfill detection + vector search

---

## 🔄 NEXT STEPS  
Start by helping me:
1. Design a proposed `xml_metadata` schema (or a hybrid extension of `exhibit_metadata`)
2. Show how this schema can support the Form 4 XML pipeline long term
3. Optionally: write a SQLAlchemy model + logging function

Let’s lock this metadata foundation before wiring it into `form4_xml_downloader.py`.
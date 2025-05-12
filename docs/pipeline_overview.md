# Safe Harbor EDGAR AI Platform – Pipeline Overview

This document outlines the major ingestion pipelines powering the Safe Harbor EDGAR AI Platform. Each pipeline is modular, testable, and focused on a specific stage of SEC filing processing.

---

## Pipeline Summary

| Pipeline | Description                                      | Entry Point                                 | Output Target                          |
|----------|--------------------------------------------------|----------------------------------------------|----------------------------------------|
| **1**    | Filing Metadata Ingestion                        | `run_daily_metadata_ingest.py`               | `filing_metadata` (Postgres table)     |
| **2**    | Filing Document Metadata (from crawler.idx)      | `run_daily_documents_ingest.py`              | `filing_documents` (Postgres table)    |
| **3**    | SGML File Download & Disk Write                  | Controlled via orchestrator (meta or batch)  | `/data/raw/sgml/[cik]/.../submission.txt` |

---

## ⛓ Pipeline Relationships

```text
        ┌────────────────────────────┐
        │  Pipeline 1: Metadata      │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Pipeline 2: Filing Docs   │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Pipeline 3: SGML Download │
        └────────────────────────────┘
```

- Each pipeline builds on outputs from the previous one.
- Pipelines are orchestrated independently, but can also be composed into a meta-orchestrator.

### Pipeline 1 – Filing Metadata Ingestion
- Goal: Ingest `crawler.idx` and extract structured `FilingMetadata`
- Collector: `FilingMetadataCollector`
- Parser: `CrawlerIdxParser`
- Writer: `FilingMetadataWriter`
- Orchestrator: `FilingMetadataOrchestrator`

```bash
python scripts/crawler_idx/run_daily_metadata_ingest.py --date YYYY-MM-DD
```

### Pipeline 2 – Filing Document Metadata
- Goal: For each `accession_number` from `filing_metadata`, fetch associated documents and write metadata
- Collector: `FilingDocumentsCollector`
- Parsers: `IndexPageParser`, `ExhibitParser`
- Writer: `FilingDocumentsWriter`
- Orchestrator: `FilingDocumentsOrchestrator`

```bash
python scripts/crawler_idx/run_daily_documents_ingest.py --date YYYY-MM-DD
```

### Pipeline 3 – SGML Download + Disk Write
- Goal: Fetch raw `.txt` submissions (SGML) and save to disk
- Downloader: `SgmlDownloader`
- Writer: `RawFileWriter` or `DocumentWriter`
- Orchestrator: `SgmlIngestionOrchestrator` (WIP or stub)

```bash
# Meta-orchestrator (planned) may invoke this
```
- ✅ Caching is supported via `SgmlDownloader(use_cache=True)`
- ✅ Files saved to: `/data/raw/sgml/[CIK]/[year]/[form_type]/[accession]/`

## Module Classification Matrix
| Component    | Layer         | Example Class                                   | Notes                                 |
| ------------ | ------------- | ----------------------------------------------- | ------------------------------------- |
| Downloader   | Downloaders   | `SgmlDownloader`                                | Optional caching, modular subclassing |
| Parser       | Parsers       | `CrawlerIdxParser`, `IndexPageParser`           | Stateless, return dataclass objects   |
| Dataclass    | Models        | `FilingMetadata`, `RawDocument`                 | Pointer vs. Container conventions     |
| Writer       | Writers       | `FilingMetadataWriter`, `FilingDocumentsWriter` | ORM persistence                       |
| Orchestrator | Orchestrators | `FilingMetadataOrchestrator`                    | Controls each pipeline                |

## Roadmap Notes
- ✅ Pipeline 1 is fully tested and production-ready.
- 🛠 Pipeline 2 is implemented and active.
- 🔄 Pipeline 3 is under active refactor to support cacheable SGML retrieval.
- 🧠 Meta-orchestrator support is being designed to coordinate Pipelines 1–3 intelligently.

## Related Documents
- `dataclass_architecture.md`
- `folder_structure.md`
- `cleaning_and_parsing.md`
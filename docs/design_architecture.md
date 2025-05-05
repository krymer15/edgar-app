
Filter out unnecessary `form_type` and `cik` values in `daily_index_metadata` layer after downloading crawler.idx?

```scss
                  [ All SGML Filings from crawler.idx ]
                                ↓
                    [ Daily SGML Index (crawler.idx) ]
                                ↓
     [ Global CIK + Form Type Filter Layer (project-level rules) ]
         - Check CIK in allowlist (market cap, sector, index)
         - Check form_type ∉ blacklist (e.g., 25-NSE, N-PX, etc)
                                ↓
             [ Store in daily_index_metadata (if passed) ]
                                ↓
      [ Parse SGML and populate parsed_sgml_metadata selectively ]
                                ↓
      [ Form-specific pipelines read parsed_sgml_metadata WHERE form_type IN (...) ]
                                ↓
            [ Log eligible XML files to xml_metadata ]
                                ↓
                 [ XML Parsing: XmlOrchestratorBase.run() ]
                                ↓
         [ Optional Post-Parse Relevance Scoring (Form 4 only) ]
                                ↓
     [ Store semantic_summary or vector only if relevant ]
```

# Technical Design Layer

```
| Layer                           | Description                                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------- |
| **CIK filter source**           | Static JSON or DB-managed list of "watched" CIKs (via market cap/index/entity type)      |
| **Form type allowlist/banlist** | Maintain `allowed_form_types` and `banned_form_types` for quick rule checks              |
| **Global filter location**      | Applied inside SGML ingestion (e.g., `ingest_sgml_batch_from_idx.py`)                    |
| **Per-pipeline filtering**      | E.g., Form 4 XML pipeline only reads from `parsed_sgml_metadata` where `form_type = '4'` |
| **Post-parse scoring**          | Form 4 XMLs get relevance scores based on transaction type, size, etc.                   |
| **URL building**                | Downstream modules construct full URLs from accession + filename as needed               |
| **Vector pipeline**             | Only vectorize XMLs with `relevant=True` tag                                             |
```
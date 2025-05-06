
flowchart TD
  %% CLI Scripts
  A1[ingest_daily_index.py] --> B1[DailyIndexOrchestrator]
  A2[ingest_from_source.py\n(--source daily_index)] --> B1
  A2b[ingest_from_source.py\n(--source submissions_api)] --> B2[SubmissionsIngestionOrchestrator]
  A3[ingest_sgml_batch_from_idx.py] --> B3[BatchSgmlIngestionOrchestrator]
  A4[run_form4_xml_ingest.py] --> B4[Form4XmlOrchestrator]

  %% Daily Index Collector
  B1 --> C1[DailyIndexCollector]
  B3 --> C1
  C1 --> D1[FilteredCikManager\n(CIK + form_type filtering)]

  %% Writers
  B1 --> E1[DailyIndexWriter.write()]
  B3 --> E1
  B3 --> E2[ParsedSgmlWriter.write()]
  B4 --> E3[XmlWriter.write()]

  %% DB Outputs
  E1 --> F1[(daily_index_metadata)]
  E2 --> F2[(parsed_sgml_metadata)]
  E3 --> F3[(xml_metadata)]

  %% Notes
  D1 -->|Skip if --skip_filter| B3

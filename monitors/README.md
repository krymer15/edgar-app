# monitors

Modules for continuous or scheduled monitoring and triggering:

- **form4_monitor.py**  
  Polls for new Form 4 filings daily and invokes ingestion.
- **filing_signal_monitor.py**  
  Watches for high-signal filings (e.g., 8-K) and triggers summarization pipelines.
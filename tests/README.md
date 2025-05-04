# Tests

Unit tests for all major modules.

## Coverage

- `test_parsed_sgml_writer.py`: Verifies DB writes and exhibit filtering
- `test_report_logger.py`: Validates CSV file creation and structure
- `test_path_manager.py`: Tests correct path building logic

## To Add (Suggestions)

- `test_sgml_filing_parser.py`: Exhibit tagging logic, primary doc inference
- `test_orchestrator.py`: Batch loop error handling, skipped filings
- `test_exhibit_summary_writer.py`: (Future GPT layer)

Run via:
```bash
pytest tests/

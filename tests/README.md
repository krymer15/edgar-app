# ✅ Tests – Safe Harbor EDGAR AI Platform

This folder contains all test modules for the core system. Tests are organized to match the structure of the app (e.g., `parsers/`, `writers/`, etc.).

---

## 🧪 How to Run Tests

### Run all tests via BAT script:
```
run_tests.bat
```

### Run a single test script:
`python -m tests.parsers.test_form4_parser`
- Use `-m` to preserve import context
- Do not use `python tests\parsers\test_form4_parser.py`

## Coverage

| File                         | Description                                  |
| ---------------------------- | -------------------------------------------- |
| `test_form4_parser.py`       | Tests XML parsing logic for Form 4           |
| `test_parsed_sgml_writer.py` | Verifies database writes + exhibit filtering |
| `test_report_logger.py`      | Validates CSV log structure                  |
| `test_path_manager.py`       | Ensures correct file path generation         |

## Skipped or Future Tests:
`tests/archived/`: Deprecated or replaced tests
`test_orchestrator.py`: Pending coverage for batch logic
`test_exhibit_summary_writer.py`: To be added with GPT summarizer integration


## Notes
Avoid running python tests/<file>.py directly — use -m to preserve import paths.

Tests can include fixture files (e.g., XML samples) in tests/parsers/fixtures/
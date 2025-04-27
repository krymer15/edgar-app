# Tests Overview

This folder contains unit tests for the `edgar-app` project.

## Test Conventions

- **Framework**: Python `unittest`
- **Network Calls**: All external HTTP requests are mocked using `unittest.mock`
- **Disk IO**: No disk writes are performed in tests
- **Environment**: Tests expect a `.env` file for loading EDGAR credentials (if necessary)
- **Speed**: All tests are designed to run quickly (<1 second per test)
- **Structure**: Each core module has a corresponding `test_*.py` file

## Running Tests

You can run all tests by:

```bash
python -m unittest discover -s tests -p "test_*.py" -v

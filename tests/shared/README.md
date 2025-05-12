# Shared Tests

This folder contains test modules for components shared across multiple pipelines, such as:

- `SgmlDownloader` — downloads and caches SEC SGML `.txt` documents
- `Path Manager`, `Report Logger`, and other utility modules
- SGML-specific data classes like `SgmlTextDocument`

## Naming Conventions

- `test_sgml_text_downloader.py`: Tests SGML `.txt` caching, cache hit logic, and return typing
- Prefixes reflect target class or module, not just filename
- Each test isolates utility logic, mocks external effects (e.g., file IO, network)

## Fixture Pathing

Tests may rely on `tests/fixtures/` for:
- Mock config files (`app_config_test.yaml`)
- Sample `.txt` documents

Make sure your `monkeypatch` or path overrides reflect those directories.


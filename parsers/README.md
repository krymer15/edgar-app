# Parsers

This folder contains logic for parsing SGML and HTML content from EDGAR filings.

## Modules

### `sgml_filing_parser.py`
- Parses raw SGML text from `.txt` files.
- Extracts:
  - Exhibit metadata (filename, description, type)
  - Primary document (guessed from HTML-like file or match to `form_type`)
- Tags exhibits as `accessible` or not based on extension or noise filters.

### `index_page_parser.py`
- Parses `index.html` (Document Format Files) to extract embedded doc links.

## Notes
- Uses strict extension filters and known noise terms.
- Diagnostics are gated behind `log_debug()` only.

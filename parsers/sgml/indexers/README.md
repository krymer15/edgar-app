# SGML Document Indexers

This folder contains logic for *indexing* SGML `.txt` submission files retrieved from EDGAR.

## Role in Pipeline 2

These indexers operate on raw `.txt` content (wrapped in `SgmlTextDocument`) and emit structured pointers to internal exhibits, primary documents, and supporting files. These pointers are represented using the `FilingDocumentMetadata` dataclass.

## Key Responsibilities

- Identify `<DOCUMENT>` blocks inside EDGAR SGML `.txt` files
- Extract tags like `<FILENAME>`, `<DESCRIPTION>`, and `<TYPE>`
- Determine document roles (e.g., is_primary, is_exhibit)
- Filter binary or non-accessible entries (e.g., `.zip`, `.exe`, etc.)
- Build canonical SEC `source_url` paths

## Output

Each document indexed is returned as a `FilingDocumentMetadata` object and eventually converted to a `FilingDocumentRecord` for database writing.

## Related Classes

- `SgmlDocumentIndexer` – Main logic for indexing SGML files
- `FilingDocumentMetadata` – Output metadata pointer class
- `FilingDocumentRecord` – Adapter destination written to the database

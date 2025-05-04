# Schemas

Typed interfaces for parsed results using Pydantic.

## Key Models

### `ParsedResultModel`
- Top-level container: `{ metadata, exhibits }`

### `ParsedMetadataModel`
- Fields: `cik`, `accession_number`, `form_type`, `filing_date`, `primary_doc_url`

### `ExhibitModel`
- Fields: `filename`, `description`, `type`, `accessible`

## Notes
- Uses `.model_dump()` (Pydantic v2) to flatten before DB write.
- Validates before `ParsedSgmlWriter` receives input.

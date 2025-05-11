# cleaners


## Cleaners vs Parsers
Yes—cleaning and parsing are two distinct steps, so it’s worth giving each its own folder and set of classes:

### Cleaning
- Goal: Take messy raw text (SGML tags, HTML markup, weird whitespace) and normalize it into plain text that’s ready for downstream parsing.
- Inputs/Outputs:
    - In: `RawDocument`
    - Out: `CleanedDocument`
- Folder: `cleaners/`
- Classes:
    - `BaseCleaner` (defines `clean(raw: RawDocument) -> CleanedDocument`)
    - `SgmlCleaner` (strip SGML headers, remove SEC boilerplate, unify line breaks)
    - `HtmlCleaner` (remove HTML tags, collapse scripts/styles)
    - `XbrlCleaner` (pretty-print XML, optionally namespace strip)

### Parsing
- Goal: Take clean text and extract structured pieces (header fields, company info, sections, financial line items).
- Inputs/Outputs:
    - In: `CleanedDocument`
    - Out: `ParsedDocument` + `ParsedChunk`
- Folder: `parsers/`
- Classes:
    - `BaseParser` (defines `parse(doc: CleanedDocument) -> Tuple[List[ParsedDocument], List[ParsedChunk]]`)
    - `SgmlParser`
    - `HtmlParser`
    - `XbrlParser`
    - `Form4Parser`, etc.
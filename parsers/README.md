# Parsers

✅ Parsing Architecture Goals
Separation of Concerns: Each parser focuses on a specific type of document or transformation.

Pluggability: New parsers can be registered or invoked dynamically.

Maintainability: Each parser is testable and loosely coupled.

Compatibility: Works well with both raw SGML and post-processed HTML/XML.

This folder contains logic for parsing SGML and HTML content from EDGAR filings.

# 🧾 SEC Filing Parsers (Safe Harbor EDGAR AI)

This module processes raw SEC EDGAR filings (SGML, HTML, XML) into structured outputs for indexing and analysis.

---

## 🔧 Fixture Loading for Parser Development

To support testing and development with real sample XML or HTML inputs, fixture files are stored outside the repo under:

`/data/raw/fixtures/`

This folder may be symlinked to an external SSD and is ignored by Git.

Use this utility to load fixtures:

```python
from utils.devtools.fixture_loader import load_fixture
xml_text = load_fixture("form4_sample.xml")
```

### 📌 Summary

| Feature                        | Status   |
|-------------------------------|----------|
| Reads from `data/raw/fixtures/` | ✅ Yes |
| Symlink-compatible             | ✅ Yes |
| Lightweight + self-contained   | ✅ Yes |
| Git-friendly                   | ✅ Yes (.gitignore applies) |

## 📦 Modules

### `base_parser.py`
Abstract base class that defines the `parse()` method signature for all specialized parsers.

### `sgml_filing_parser.py`
Parses `.txt` SGML filings to extract:
- Exhibit filenames, types, and descriptions
- Primary document heuristics

### `index_page_parser.py`
Extracts the primary embedded document URL from the `index.html` page (Document Format Files).

### `exhibit_parser.py`
Cleans HTML exhibit files, strips tables, and adds `[HEADER]` tags for NLP preprocessing.

---

## 🧩 Specialized Form Parsers (`parsers/forms/`)

- `form4_parser.py`: Parses XML Form 4 insider transaction filings into structured data.
- Extendable: Add Form 10-K, S-1, 13F, etc.

---

## 🚦 Filing Router (`parsers/router/`)

Routes each filing to the appropriate parser based on form type and document format.

---

## 🛠️ Usage

```python
from parsers.router.filing_router import FilingRouter

router = FilingRouter()
parsed = router.route("4", xml_content)


---

### 💡 About Parser Registry
The registry is just a dictionary behind the scenes. The optional `@register_parser` decorator approach is more dynamic and avoids hardcoding, but for now, **your current router pattern is fine** and avoids bloat.


## Notes
- Uses strict extension filters and known noise terms.
- Diagnostics are gated behind `log_debug()` only.

| Layer | Parser Type                          | Responsibility                                                                                                           |
| ----- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| L1    | `SgmlFilingParser`                   | Parse `<DOCUMENT>` blocks from SGML `.txt` filings. Extract exhibit metadata, flag accessibility, guess primary document |
| L2    | `IndexPageParser`                    | Parse `index.html` to get embedded doc URLs or check anchor structure                                                    |
| L2    | `ExhibitParser`                      | Clean and annotate exhibit HTML                                                                                          |
| L3    | `Form4Parser`, `Form10KParser`, etc. | Custom logic for specific form types (XML Form 4, XBRL 10-K, etc.)                                                       |
| L4    | `FilingRouter` (new)                 | Route to appropriate parser(s) based on form type and extension (e.g., XML → Form 4 XML parser)                          |

## Sample Form 4 Pipeline
L1 – SGML Layer
| Stage | Component               | Role                                                  |
| ----- | ----------------------- | ----------------------------------------------------- |
| 1.1   | `SgmlFilingParser`      | Parses raw `.txt` SGML to extract `<DOCUMENT>` blocks |
| 1.2   | `parsed_sgml_writer.py` | Persists parsed metadata and exhibit structure        |
| 1.3   | `ExhibitMetadata`       | Flags `.xml` exhibit of interest (e.g. Form 4 XML)    |

L2 – Exhibit Resolution Layer
| Stage | Component                      | Role                                           |
| ----- | ------------------------------ | ---------------------------------------------- |
| 2.1   | `IndexPageParser` *(optional)* | Parses `index.html` for anchor link resolution |
| 2.2   | `ExhibitParser` *(optional)*   | Cleans HTML tables, flags accessibility issues |
| 2.3   | Exhibit Handler (logic)        | Downloads `.xml` Form 4 document to disk       |

L3 – Form-Specific Parser
| Stage | Component         | Role                                                             |
| ----- | ----------------- | ---------------------------------------------------------------- |
| 3.1   | `Form4Parser`     | Parses key issuer, owner, and transaction fields from Form 4 XML |
| 3.2   | `form4_writer.py` | Persists parsed results to Postgres (via ORM)                    |

L4 – Filing Router + Orchestrator
| Stage | Component              | Role                                                                |
| ----- | ---------------------- | ------------------------------------------------------------------- |
| 4.1   | `FilingParserManager`  | Routes content to correct parser (`Form4Parser`) based on form type |
| 4.2   | `Form4XmlOrchestrator` | Coordinates: ingest XML → route → write → log                       |

### Thoughts on two-layer Parser interface:

```python
class FilingParser:
    def parse(self, filing_text: str) -> ParsedFiling:
        pass

class HTMLFilingParser(FilingParser):
    def parse(self, filing_text: str) -> ParsedFiling:
        # HTML parsing logic
        pass

class SGMLFilingParser(FilingParser):
    def parse(self, filing_text: str) -> ParsedFiling:
        # SGML parsing logic (later or stub for now)
        pass
```

#### pipeline integration
```rust
Raw Filing -> ParserSelector (HTML or SGML) -> FilingParser -> ParsedFiling (text blocks, exhibits, metadata) -> Storage
```
